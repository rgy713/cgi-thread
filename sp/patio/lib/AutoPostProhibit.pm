package AutoPostProhibit;
use strict;

use open IO => ':encoding(cp932)';

use Carp qw(croak confess);
use Encode qw();
use HTML::Entities qw();
use Scalar::Util qw(blessed);
use List::MoreUtils qw(uniq);

use Matcher::Utils;

my Encode::Encoding $enc_cp932 = defined($main::enc_cp932) ? $main::enc_cp932 : Encode::find_encoding('cp932');

my $disable_setting_char = $enc_cp932->decode('▼');
my $multiple_submissions_count_log_delimiter = '<>';
my $old_thread_age_count_log_delimiter = '<>';

my $under_threshold_char = $enc_cp932->decode('▼');
my $over_threshold_char = $enc_cp932->decode('▲');

# 判定結果定数定義
use constant {
    RESULT_ALL_PASSED                      => 0,
    RESULT_THREAD_CREATE_SUPPRESS_REQUIRED => 1,
    RESULT_REDIRECT_REQUIRED               => 1 << 1
};

# 自動書き込み禁止ログ ヘッダー定義
my @log_header = map { $enc_cp932->decode($_); } (
    '日時', 'CookieA発行', 'プライベート判定', '一致時間', '期間指定', 'ステータス',
    'スレタイ除外', '除外', '強制', 'URL', 'カテゴリ', '■', '一致スレタイ', 'スレタイ部分の除外',
    '一致スレタイ（抑制）', '一致レス（抑制）', '■', '一致名前', '■', '文字数', '対象のレス',
    '一致レス', '文字数除外', '指定レス番までの一致レス', '文字数除外', '複数回レス', '古スレage', '■',
    'スレ作成時のスレタイによるレスの除外（スレ）', 'スレ作成時のスレタイによるレスの除外（レス）',
    'スレタイによるレスの除外（スレ）', 'スレタイによるレスの除外（レス）', '指定レスまで除外', '■',
    'スレ作成時のスレタイ強制一致', 'スレ作成時の強制一致レス（スレ）', 'スレ作成時の強制一致レス（レス）',
    'スレタイによる強制一致レス（スレ）', 'スレタイによる強制一致レス（レス）', '画像アップ', '■',
    '一致CookieA', '一致登録ID', '一致書込ID', '一致ホスト', '一致UserAgent', '一致MD5', '一致画像コメント', '■',
    'スレタイ', '名前', 'レス内容', '画像枚数', 'プライベート',
    'CookieA', '登録ID', '書込ID', 'ホスト', 'UserAgent', 'タイムスタンプ', 'ID'
);

# 自動書き込み禁止ログ 2行目ヘッダー定義
my $log_second_header_row = $enc_cp932->decode(
    'AA,yy,BB,CC,zz,DD,ww,EE,FF,GG,HH,■,II,JJ,KK,LL,■,MM,■,xx,NN,OO,WW,PP,aaa,QQ,RR,■,SS,TT,YY,VV,bbb,■,XX,YY,ZZ,aa,bb,cc,■,dd,ee,ff,gg,hh,ii,jj,■,kk,ll,mm,nn,oo,pp,qq,rr,ss,tt,uu,vv'
);

# 引数チェックサブルーチン定義
sub arg_check {
    my ($require_num_of_args, $require_ref_type_of_args_array_ref, @args) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }

    my $num_of_args = scalar(@args) || 0;
    if ($num_of_args != $require_num_of_args) {
        confess(sprintf('wrong number of arguments (%d for %d)', $num_of_args, $require_num_of_args));
    } elsif (defined($require_ref_type_of_args_array_ref)) {
        my @err_ref_type_indexes = grep {
            defined(${$require_ref_type_of_args_array_ref}[$_])
                && ref($args[$_]) ne ${$require_ref_type_of_args_array_ref}[$_]
        } (0 .. $require_num_of_args);
        if (scalar(@err_ref_type_indexes) > 0) {
            confess('wrong ref type argument passed: index ' . join(', ', @err_ref_type_indexes));
        }
    }
};

sub new {
    my $class = shift;
    my ($matcher_utils_instance,
        $setting_filepath, $log_path, $no_delete_log_path, $thread_number_res_target_log_path, $thread_title_res_target_log_path,
        $multiple_submissions_count_log_path, $old_thread_age_count_log_path,
        $category_set_array_ref, $log_concat_url,
        $exempting_name, $additional_match_required_host_array_ref, $log_delete_time, $up_to_res_number_setting_array_ref,
        $thread_number_res_target_hold_hour_1,$thread_number_res_target_hold_hour_2,$thread_number_res_target_hold_hour_3,
        $thread_number_res_target_hold_hour_4,$thread_number_res_target_hold_hour_5,$thread_number_res_target_hold_hour_6,
        $thread_title_res_target_restrict_keyword_array_ref, $thread_title_res_target_restrict_exempt_keyword_array_ref, $thread_title_res_target_hold_hour_array_ref,
        $combination_img_md5_array_ref,
        $multiple_submissions_setting_array_ref, $multiple_submissions_redirect_threshold, $multiple_submissions_log_hold_minutes,
        $multiple_submissions_log_not_record_host_array_ref,
        $old_thread_age_setting_array_ref, $old_thread_age_redirect_threshold, $old_thread_age_log_hold_minutes,
        $old_thread_age_log_not_record_host_array_ref,
        $time, $date, $host, $useragent, $cookie_a, $user_id, $history_id, $is_private_browsing_mode,
        $cookie_a_instance, $cookie_a_issuing_flag) = @_;
    arg_check(
        42,
        [
            'Matcher::Utils',
            '', '', '', '', '',
            '', '',
            'ARRAY', '',
            '', 'ARRAY', '', 'ARRAY',
            '', '', '',
            '', '', '',
            'ARRAY', 'ARRAY', 'ARRAY',
            'ARRAY',
            'ARRAY', '', '',
            'ARRAY',
            'ARRAY', '', '',
            'ARRAY',
            '', '', '', '', '', '', '', '',
            'UniqueCookie', ''
        ],
        @_
    );

    # Matcher::Utilsインスタンス取得
    my Matcher::Utils $mu = $matcher_utils_instance;

    # スレッドタイトル/カテゴリ名置き換えセット取得
    my @category_set;
    foreach my $conv_set_str (@{$category_set_array_ref}) {
        my $decoded_conv_set_str = $enc_cp932->decode($conv_set_str);
        my ($keyword, $category) = split(/:/, $decoded_conv_set_str, 2);
        if ($keyword eq '' || $category eq '') {
            next;
        }
        push(@category_set, [$keyword, $category]);
    }

    # スレッドNoを自動書き込み禁止機能のレス部分相当で動作する機能 制限時間配列作成
    my @thread_number_res_target_hold_hours = (
        undef, # type値をそのままindexとするためのdummy要素
        $thread_number_res_target_hold_hour_1,
        $thread_number_res_target_hold_hour_2,
        $thread_number_res_target_hold_hour_3,
        $thread_number_res_target_hold_hour_4,
        $thread_number_res_target_hold_hour_5,
        $thread_number_res_target_hold_hour_6
    );

    my %self = (
        CALL_CHECK_FLAG                                           => undef,
        MATCHER_UTILS_INSTANCE                                    => $matcher_utils_instance,
        CATEGORY_SET                                              => \@category_set,
        LOG_CONCAT_URL                                            => $log_concat_url,
        EXEMPTING_NAME                                            => $exempting_name,
        UP_TO_RES_NUMBER_SETTING_ARRAY_REF                        => $up_to_res_number_setting_array_ref,
        THREAD_NUMBER_RES_TARGET_HOLD_HOURS_ARRAY_REF             => \@thread_number_res_target_hold_hours,
        THREAD_TITLE_RES_TARGET_RESTRICT_KEYWORD_ARRAY_REF        => $thread_title_res_target_restrict_keyword_array_ref,
        THREAD_TITLE_RES_TARGET_RESTRICT_EXEMPT_KEYWORD_ARRAY_REF => $thread_title_res_target_restrict_exempt_keyword_array_ref,
        THREAD_TITLE_RES_TARGET_RESTRICT_HOLD_HOUR_ARRAY_REF      => $thread_title_res_target_hold_hour_array_ref,
        COMBINATION_IMG_MD5_ARRAY_REF                             => $combination_img_md5_array_ref,
        MULTIPLE_SUBMISSIONS_SETTING_ARRAY_REF                    => $multiple_submissions_setting_array_ref,
        MULTIPLE_SUBMISSIONS_REDIRECT_THRESHOLD                   => $multiple_submissions_redirect_threshold,
        OLD_THREAD_AGE_SETTING_ARRAY_REF                          => $old_thread_age_setting_array_ref,
        OLD_THREAD_AGE_REDIRECT_THRESHOLD                         => $old_thread_age_redirect_threshold,
        TIME                                                      => $time,
        DATE                                                      => $date,
        HOST                                                      => $host,
        USERAGENT                                                 => $useragent,
        COOKIE_A                                                  => $cookie_a,
        USER_ID                                                   => $user_id,
        HISTORY_ID                                                => $history_id,
        IS_PRIVATE_BROWSING_MODE                                  => $is_private_browsing_mode,
        COOKIE_A_INSTANCE                                         => $cookie_a_instance,
        COOKIE_A_ISSUING_FLAG                                     => $cookie_a_issuing_flag
    );

    # 外部ファイルをパースし、有効な設定を読み込み
    my @validsetting_and_userinfo_matchresult;

    # 外部ファイルオープン
    open(my $setting_fh, '<', $setting_filepath) || croak("Open error: $setting_filepath");
    flock($setting_fh, 1) || croak("Lock error: $setting_filepath");
    $self{SETTING_FH} = $setting_fh;

    # ヘッダ行(2行)読み飛ばし
    <$setting_fh>;
    <$setting_fh>;

    # 外部ファイルをパースし、有効な設定を読み込み
    while (my $line = <$setting_fh>) {
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @settings = split(/\^/, $line, - 1);
        if (scalar(@settings) != 38 || $settings[1] eq $disable_setting_char) {
            # 38列ではないログ行、もしくは、無効列に▼の列はスキップ
            next;
        }

        # ホストとUserAgent・CookieA or 登録ID or 書込ID・プライベートモード・時間範囲指定・期間指定・画像列について、
        # 「-」を空文字列に置き換える
        foreach my $i (2 .. 6, 31) {
            $settings[$i] =~ s/^-$//;
        }

        # プライベートモード列が1の場合に対象判定
        my $private_browsing_mode_match_flag;
        if ($settings[4] eq '1') {
            if ($is_private_browsing_mode) {
                $private_browsing_mode_match_flag = 1;
            } else {
                next;
            }
        }

        # 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」のいずれかで一致したかどうかのフラグ
        my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;

        # ホストとUserAgentの一致判定
        my @host_useragent_match_array = ([], []);
        if ($settings[2] ne '') {
            my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $settings[2], ['**', '**'], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (defined($host_useragent_match_array_ref)) {
                @host_useragent_match_array = @{$host_useragent_match_array_ref};
                $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
            }
        }

        # CookieA or 登録ID or 書込IDの一致判定
        my @cookiea_userid_historyid_match_array = ([], [], []);
        if ($settings[3] ne '') {
            my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $settings[3], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (defined($cookiea_userid_historyid_match_array_ref)) {
                @cookiea_userid_historyid_match_array = @{$cookiea_userid_historyid_match_array_ref};
                $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
            }
        }

        # 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」の
        # どちらかで一致していないときは、スキップ
        if ($host_useragent_or_cookiea_userid_historyid_matched_flg == 0) {
            next;
        }

        # 時間範囲指定の一致判定
        my @match_time_range_array;
        if ($settings[5] ne '') {
            if ($mu->is_in_time_range($settings[5], undef())) {
                @match_time_range_array = ($settings[5]);
            } else {
                next;
            }
        }

        # 期間指定・経過時間の一致判定
        if ($settings[6] ne '' && $settings[7] ne '') {
            if (!$mu->is_within_validity_period($settings[6], $settings[7], undef())) {
                next;
            }
        }

        # 設定値と「ホストとUserAgent」・「CookieA or 登録ID or 書込ID」・「時間範囲」の一致結果を
        # 有効設定・ユーザー情報配列に格納
        push(@validsetting_and_userinfo_matchresult,
            [
                \@settings,
                $host_useragent_match_array[0], # ホスト
                $host_useragent_match_array[1], # 一致UserAgent
                $cookiea_userid_historyid_match_array[0], # 一致CookieA
                $cookiea_userid_historyid_match_array[1], # 一致登録ID
                $cookiea_userid_historyid_match_array[2], # 一致書込ID
                \@match_time_range_array, # 一致時間範囲
                $private_browsing_mode_match_flag # プライベートブラウジングモード対象設定で一致したかどうか
            ]
        );
    }
    $self{VALIDSETTING_AND_USERINFO_MATCHRESULT} = \@validsetting_and_userinfo_matchresult;

    # 自動書き込み禁止ログオープン
    my $new_log_flag = !-f $log_path || -s $log_path == 0;
    my $new_no_delete_log_flag = !-f $no_delete_log_path || -s $no_delete_log_path == 0;
    my ($log_fh, $no_delete_log_fh);
    if (!((open($log_fh, '+<', $log_path) || open($log_fh, '>', $log_path)) && flock($log_fh, 2))) {
        croak("Open or Lock error: $log_path");
    }
    if (!(open($no_delete_log_fh, '>>', $no_delete_log_path) && flock($no_delete_log_fh, 2))) {
        croak("Open or Lock error: $no_delete_log_path");
    }
    %self = (
        %self,
        NEW_LOG_FLAG           => $new_log_flag,
        NEW_NO_DELETE_LOG_FLAG => $new_no_delete_log_flag,
        LOG_FH                 => $log_fh,
        NO_DELETE_LOG_FH       => $no_delete_log_fh,
    );

    # 自動書き込み禁止ログに同一ホスト/CookieA/登録ID/書込IDが含まれるかチェック
    # (ログファイル新規作成時にはチェックしない)
    my $read_log_contents = '';
    my ($read_skip_flag, $log_exist_host_flag, $log_exist_cookiea_flag, $log_exist_userid_flag, $log_exist_historyid_flag);
    if (!$new_log_flag) {
        # ログ 項目インデックス取得
        my ($title_exempt_index, $exempt_index, $cookiea_index, $userid_index, $historyid_index, $host_index, $timestamp_index);
        {
            my ($find_title_exempt, $find_exempt, $find_cookiea, $find_userid, $find_historyid, $find_host, $find_timestamp)
                = map { $enc_cp932->decode($_) } ('スレタイ除外', '除外', 'CookieA', '登録ID', '書込ID', 'ホスト', 'タイムスタンプ');
            ($title_exempt_index) = grep { $log_header[$_] eq $find_title_exempt } 0 .. $#log_header;
            ($exempt_index) = grep { $log_header[$_] eq $find_exempt } 0 .. $#log_header;
            ($cookiea_index) = grep { $log_header[$_] eq $find_cookiea } 0 .. $#log_header;
            ($userid_index) = grep { $log_header[$_] eq $find_userid } 0 .. $#log_header;
            ($historyid_index) = grep { $log_header[$_] eq $find_historyid } 0 .. $#log_header;
            ($host_index) = grep { $log_header[$_] eq $find_host } 0 .. $#log_header;
            ($timestamp_index) = grep { $log_header[$_] eq $find_timestamp } 0 .. $#log_header;
        }

        # ホスト無視・リダイレクト判定要素追加 対象ホストに中間一致した時はフラグを立てる
        my $ignore_host_in_log_matching_flag;
        foreach my $partial_hostname (@{$additional_match_required_host_array_ref}) {
            if (index($host, $partial_hostname) != - 1) {
                $ignore_host_in_log_matching_flag = 1;
                last;
            }
        }

        # 「除外」一致のため、内部エンコードに変換
        my $decoded_exempt_str = $enc_cp932->decode('除外');

        # 自動書き込み禁止ログ 読み込み・判定
        seek($log_fh, 0, 0); # ファイルポインタを先頭に移動
        <$log_fh>; # 先頭行読み飛ばし
        <$log_fh>; # 2行目読み飛ばし
        while (my $line = <$log_fh>) {
            $line =~ s/(?:\r\n|\r|\n)$//;
            my @row = split(/,/, $line);

            # 不正行・自動消去時間を経過したログ行を判定から除外
            if (scalar(@row) != scalar(@log_header)
                || ($log_delete_time != 0 && $row[$timestamp_index] + $log_delete_time < $time)) {
                $read_skip_flag ||= 1;
                next;
            }

            # スレタイ除外列と除外列が「除外」ではないログ行のみ判定を行う
            if ($row[$title_exempt_index] ne $decoded_exempt_str && $row[$exempt_index] ne $decoded_exempt_str) {
                # 完全一致するホストが見つかった時はフラグを立てる
                if (!$ignore_host_in_log_matching_flag && $row[$host_index] eq $host) {
                    $log_exist_host_flag ||= 1;
                }

                # 完全一致するCookieAが見つかった時はフラグを立てる
                if ($row[$cookiea_index] ne '' && $row[$cookiea_index] eq $cookie_a) {
                    $log_exist_cookiea_flag ||= 1;
                }

                # 完全一致する登録IDが見つかったときはフラグを立てる
                if ($row[$userid_index] ne '' && $row[$userid_index] eq $user_id) {
                    $log_exist_userid_flag ||= 1;
                }

                # 完全一致する書込IDが見つかったときはフラグを立てる
                if ($row[$historyid_index] ne '' && $row[$historyid_index] eq $history_id) {
                    $log_exist_historyid_flag ||= 1;
                }
            }

            # ログ行を残す
            $read_log_contents .= "$line\n";
        }
    }
    %self = (
        %self,
        READ_LOG_CONTENTS        => $read_log_contents,
        READ_SKIP_FLAG           => $read_skip_flag,
        LOG_EXIST_HOST_FLAG      => $log_exist_host_flag,
        LOG_EXIST_COOKIEA_FLAG   => $log_exist_cookiea_flag,
        LOG_EXIST_USERID_FLAG    => $log_exist_userid_flag,
        LOG_EXIST_HISTORYID_FLAG => $log_exist_historyid_flag
    );

    # スレッドNoを自動書き込み禁止機能のレス部分相当で動作する機能
    # ログファイルパース処理
    my @thread_number_res_target;
    if (-s $thread_number_res_target_log_path > 2) {
        # ログファイル読み込み・パース処理
        my $json_log_fh;
        if (open($json_log_fh, '<:utf8', $thread_number_res_target_log_path) && flock($json_log_fh, 1)) {
            # ログファイルを一度に読み込む
            seek($json_log_fh, 0, 0);
            local $/;
            my $json_log_contents = <$json_log_fh>;
            close($json_log_fh);

            # JSONパースを行う (内容が異常の場合はスキップ)
            eval {
                my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
                if (ref($json_parsed_ref) eq 'ARRAY') {
                    @thread_number_res_target = @{$json_parsed_ref};
                }
            };
        }
    }
    $self{THREAD_NUMBER_RES_TARGET_ARRAY_REF} = \@thread_number_res_target;

    # スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能
    # ログファイルパース処理
    my @thread_title_res_target;
    if (-s $thread_title_res_target_log_path > 2) {
        # ログファイル読み込み・パース処理
        my $json_log_fh;
        if (open($json_log_fh, '<:utf8', $thread_title_res_target_log_path) && flock($json_log_fh, 1)) {
            # ログファイルを一度に読み込む
            seek($json_log_fh, 0, 0);
            local $/;
            my $json_log_contents = <$json_log_fh>;
            close($json_log_fh);

            # JSONパースを行う (内容が異常の場合はスキップ)
            eval {
                my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
                if (ref($json_parsed_ref) eq 'ARRAY') {
                    @thread_title_res_target = @{$json_parsed_ref};
                }
            };
        }
    }
    $self{THREAD_TITLE_RES_TARGET_ARRAY_REF} = \@thread_title_res_target;

    # 複数回投稿時の自動書き込み禁止機能
    # ログファイルパース処理
    my $multiple_submissions_count_log_fh;
    my @multiple_submissions_validlog;
    open($multiple_submissions_count_log_fh, '+<', $multiple_submissions_count_log_path)
        || open($multiple_submissions_count_log_fh, '>', $multiple_submissions_count_log_path)
        || croak("Open error: $multiple_submissions_count_log_path");
    flock($multiple_submissions_count_log_fh, 2) || croak("Lock error: $multiple_submissions_count_log_path");
    seek($multiple_submissions_count_log_fh, 0, 0);
    while (my $line = <$multiple_submissions_count_log_fh>) {
        # 改行文字を除き、<>で分割
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @log = split(/$multiple_submissions_count_log_delimiter/, $line);

        # 5項目存在しないか、消去時間を経過しているログ行はスキップ
        if (scalar(@log) != 5  || ($log[4] + $multiple_submissions_log_hold_minutes * 60) < $time) {
            next;
        }

        # 有効ログ配列に追加
        push(@multiple_submissions_validlog, \@log);
    }
    seek($multiple_submissions_count_log_fh, 0, 0);
    $self{MULTIPLE_SUBMISSIONS_COUNT_LOG_FH} = $multiple_submissions_count_log_fh;
    $self{MULTIPLE_SUBMISSIONS_VALIDLOG_ARRAY_REF} = \@multiple_submissions_validlog;

    # 複数回投稿時の自動書き込み禁止機能
    # ユーザーカウントログ ホスト記録判定
    my $multiple_submissions_log_record_host_flag = 1;
    foreach my $exclude_host (@{$multiple_submissions_log_not_record_host_array_ref}) {
        if (index($host, $exclude_host) >= 0) {
            $multiple_submissions_log_record_host_flag = 0;
            last;
        }
    }
    $self{MULTIPLE_SUBMISSIONS_LOG_RECORD_HOST_FLAG} = $multiple_submissions_log_record_host_flag;

    # 古スレageの自動書き込み禁止機能
    # ログファイルパース処理
    my $old_thread_age_count_log_fh;
    my @old_thread_age_validlog;
    open($old_thread_age_count_log_fh, '+<', $old_thread_age_count_log_path)
        || open($old_thread_age_count_log_fh, '>', $old_thread_age_count_log_path)
        || croak("Open error: $old_thread_age_count_log_path");
    flock($old_thread_age_count_log_fh, 2) || croak("Lock error: $old_thread_age_count_log_path");
    seek($old_thread_age_count_log_fh, 0, 0);
    while (my $line = <$old_thread_age_count_log_fh>) {
        # 改行文字を除き、<>で分割
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @log = split(/$old_thread_age_count_log_delimiter/, $line);

        # 5項目存在しないか、消去時間を経過しているログ行はスキップ
        if (scalar(@log) != 5  || ($log[4] + $old_thread_age_log_hold_minutes * 60) < $time) {
            next;
        }

        # 有効ログ配列に追加
        push(@old_thread_age_validlog, \@log);
    }
    seek($old_thread_age_count_log_fh, 0, 0);
    $self{OLD_THREAD_AGE_COUNT_LOG_FH} = $old_thread_age_count_log_fh;
    $self{OLD_THREAD_AGE_VALIDLOG_ARRAY_REF} = \@old_thread_age_validlog;

    # 古スレageの自動書き込み禁止機能
    # 古スレageユーザーカウントログ ホスト記録判定
    my $old_thread_age_log_record_host_flag = 1;
    foreach my $exclude_host (@{$old_thread_age_log_not_record_host_array_ref}) {
        if (index($host, $exclude_host) >= 0) {
            $old_thread_age_log_record_host_flag = 0;
            last;
        }
    }
    $self{OLD_THREAD_AGE_LOG_RECORD_HOST_FLAG} = $old_thread_age_log_record_host_flag;

    # クロージャ定義
    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }
        my $num_of_args = scalar(@_);
        if ($num_of_args != 1 && $num_of_args != 2) {
            confess(sprintf('wrong number of arguments (%d for 1 or 2)', $num_of_args));
        }
        my $key = shift;
        if (!exists($self{$key})) {
            confess("key not found: $key");
        }
        if ($num_of_args == 1) {
            # 引数として与えられたキーに対応する値を返す
            return $self{$key};
        } else {
            # 引数として与えられたキーに値をセットし、その値をそのまま返す
            my $set_value = shift;
            $self{$key} = $set_value;
            return $self{$key};
        }
    };

    return bless $closure, $class;
}

sub DESTROY {
    my $self = shift;

    # 外部ファイルハンドラ クローズ
    my $setting_fh = $self->('SETTING_FH');
    close($setting_fh);
}

sub prohibit_post_check {
    my $self = shift;
    my ($new_thread_flag, $age_flag, $thread_no, $new_res_no, $name, $title, $res, $upfile_count,
        $image_md5_array_ref_array_ref, $idcrypt, $log_array_ref, $threadlog_same_user_found_flag_in_suppress_thread_creation) = @_;
    if (!defined(blessed($self)) || !$self->isa('AutoPostProhibit')) {
        confess('call me only in instance variable.');
    }
    arg_check(12, ['', '', '', '', '', '', '', '', 'ARRAY', '', 'ARRAY', ''], @_);

    # ログ読み込みは1度しか行わないため、複数回の判定を行うことは想定していない
    if ($self->('CALL_CHECK_FLAG')) {
        confess('this subroutine can be called only once.');
    } else {
        $self->('CALL_CHECK_FLAG', 1);
    }

    # Matcher::Utilsインスタンス取得
    my Matcher::Utils $mu = $self->('MATCHER_UTILS_INSTANCE');

    my ($private_browsing_mode_matched_flag);

    # スレッドタイトル カテゴリ列一致判定・置き換え
    my $category = '';
    my $category_removed_title = $title;
    foreach my $conv_set_ref (@{$self->('CATEGORY_SET')}) {
        my ($keyword, $cat) = @{$conv_set_ref};
        my $capture_regex = '^(.*)' . quotemeta($keyword) . '$';
        if ($title =~ /$capture_regex/) {
            # カテゴリ名をセット
            $category = $cat;
            # スレッド名をカテゴリ名を除いたもので置き換え
            $category_removed_title = $1;
            last;
        }
    }

    # >>1のレス内容を取り出す
    my $first_res = ${${$log_array_ref}[1]}[4];

    # レス文字数を取得
    my $res_length = do {
        my $normalized_res = $res;
        $normalized_res =~ s/<br>//g;
        $normalized_res = HTML::Entities::decode($normalized_res);
        length($normalized_res);
    };

    # 外部ファイルで設定を定義している自動書き込み禁止機能関連の判定
    # 一致結果配列の定義
    my @match_res_exempt_on_thread_create = ([], []);
    my @match_title_exempt_on_thread_create = ();
    my @match_res_exempt_on_res = ([], [], []);
    my @match_name = ([], []);
    my @match_suppress_thread_creation = ([], []);
    my @match_title = ();
    my @match_res = ([], [], []);
    my @force_res_match_on_thread_create = ([], [], '');
    my @force_res_match_on_res = ([], []);
    my @force_title_match_on_thread_create = ();
    my @match_host = ();
    my @match_useragent = ();
    my @match_cookiea = ();
    my @match_userid = ();
    my @match_historyid = ();
    my @match_time_range = ();
    my @match_period = ();
    # 自動書き込み禁止機能(レス)で一致した設定行の文字数除外設定の配列の定義
    my @valid_exempt_res_length_settings;
    foreach my $validsetting_and_userinfo_matchresult_array_ref (@{$self->('VALIDSETTING_AND_USERINFO_MATCHRESULT')}) {
        # 行の設定のいずれかに一致したかどうかのフラグ
        my $match_flag;

        # 設定を取得
        my @settings = @{${$validsetting_and_userinfo_matchresult_array_ref}[0]};

        # スレッド作成抑制機能・自動書き込み禁止機能のスレッド作成時のレスの除外機能
        # 判定項目: スレッドタイトル, レス内容
        # (新規スレッド作成時のみ判定を行う)
        if ($new_thread_flag && $settings[20] ne '' && $settings[21] ne '') {
            # スレッドタイトルとレス内容の一致判定
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[20]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[21]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            # 文字数除外判定 (指定がない場合は判定を行わない)
            my $res_length_exempt_match_or_pass_flag = $settings[22] ne '' ? $settings[22] <= $res_length : 1;

            if (defined($title_match_array_ref) && defined($res_match_array_ref) && $res_length_exempt_match_or_pass_flag) {
                # 一致したスレッドタイトル・レスを取り出す
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # 一致結果配列に追加し、ユニーク化を行う
                @match_res_exempt_on_thread_create = (
                    [uniq(@{$match_res_exempt_on_thread_create[0]}, @title_match_array)], # 一致スレッドタイトル
                    [uniq(@{$match_res_exempt_on_thread_create[1]}, @res_match_array)]    # 一致レス内容
                );

                # 行設定一致フラグを立てる
                $match_flag ||= 1;
            }
        }

        # スレッド作成抑制機能・自動書き込み禁止機能(共にスレッドタイトル部分)の除外機能
        # 判定項目: スレッドタイトル
        # (新規スレッド作成時のみ判定を行う)
        if ($new_thread_flag && $settings[19] ne '') {
            # スレッドタイトルとレス内容の一致判定
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[19]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref)) {
                # 一致したスレッドタイトルを取り出す
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};

                # 一致結果配列に追加し、ユニーク化を行う
                @match_title_exempt_on_thread_create = uniq(@match_title_exempt_on_thread_create, @title_match_array);

                # 行設定一致フラグを立てる
                $match_flag ||= 1;
            }
        }

        # 自動書き込み禁止機能のスレッドタイトルによるレスの除外機能
        # 判定項目: スレッドタイトル, レス内容, 指定レスまで除外(指定時のみ)
        # (レス時のみ判定を行う)
        if (!$new_thread_flag && $settings[24] ne '' && $settings[25] ne '') {
            # スレッドタイトルとレス内容の一致判定
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[24]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[25]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref) && defined($res_match_array_ref)) {
                # 一致したスレッドタイトル・レスを取り出す
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # 指定したレスまで除外 判定
                my @exempt_up_to_res_match;
                if ($settings[26] ne '') {
                    my $exempt_up_to_res_num = int($settings[26]);
                    if ($new_res_no <= $exempt_up_to_res_num) {
                        # 除外対象のため、そのまま配列に追加
                        @exempt_up_to_res_match = ($exempt_up_to_res_num);
                    } else {
                        # レスNoが設定値より大きく、除外対象外レスの場合、
                        # ▲を先頭に付与して配列に追加 (除外判定時にはこの値は除外する)
                        @exempt_up_to_res_match = ($over_threshold_char . $exempt_up_to_res_num);
                    }
                }

                # 一致結果配列に追加
                push(@{$match_res_exempt_on_res[0]}, @title_match_array);      # 一致スレッドタイトル
                push(@{$match_res_exempt_on_res[1]}, @res_match_array);        # 一致レス内容
                push(@{$match_res_exempt_on_res[2]}, @exempt_up_to_res_match); # 指定したレスまで除外 設定

                # 行設定一致フラグを立てる
                $match_flag ||= 1;
            }
        }

        # 自動書き込み禁止機能(名前)
        # 判定項目: スレッドタイトル(一致時先頭@ 付加), 名前
        # (自動書き込み禁止機能の名前欄の除外機能の除外設定に一致しなかった場合のみ、判定を行う)
        if ($settings[36] ne '' && $settings[37] ne ''
            && !defined($mu->universal_match([$name], [$self->('EXEMPTING_NAME')], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)))
        {
            # スレッドタイトル・名前の一致判定
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[36], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            my $name_match_array_ref = $mu->universal_match([$name], [$settings[37]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref) && defined($name_match_array_ref)) {
                # 一致したスレッドタイトル・名前を取り出す
                my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                my @name_match_array = map { ${$_}[0] } @{${$name_match_array_ref}[0]};

                # 一致結果配列に追加し、ユニーク化を行う
                @match_name = (
                    [uniq(@{$match_name[0]}, @title_match_array)], # 一致スレッドタイトル
                    [uniq(@{$match_name[1]}, @name_match_array)]   # 一致した名前
                );

                # 行設定一致フラグを立てる
                $match_flag ||= 1;
            }
        }

        # スレッド作成抑制機能
        # 判定項目: スレッドタイトル, レス内容
        # (新規スレッド作成時のみ判定を行う)
        if ($new_thread_flag && !$threadlog_same_user_found_flag_in_suppress_thread_creation) {
            # スレ作成抑制（スレタイ）・スレ作成抑制（レス）列判定
            if ($settings[10] ne '') {
                # スレッドタイトルの一致判定
                my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[10], '', undef(), '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};

                # レス内容の一致判定 (指定がある場合のみ)
                my $res_match_array_ref;
                if ($settings[11] ne '') {
                    $res_match_array_ref = $mu->universal_match([$res], [$settings[11]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
                }

                if (defined($title_match_array_ref) && ($settings[11] eq '' || defined($res_match_array_ref))) {
                    # 一致したスレッドタイトル・レスを取り出す
                    my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                    my @res_match_array = defined($res_match_array_ref) ? map { ${$_}[0] } @{${$res_match_array_ref}[0]} : ();

                    # 一致結果配列に追加し、ユニーク化を行う
                    @match_suppress_thread_creation = (
                        [uniq(@{$match_suppress_thread_creation[0]}, @title_match_array)], # 一致スレッドタイトル
                        [uniq(@{$match_suppress_thread_creation[1]}, @res_match_array)]    # 一致レス内容
                    );

                    # 行設定一致フラグを立てる
                    $match_flag ||= 1;
                }
            }

            # スレ作成抑制（スレタイのみ）列判定
            if ($settings[9] ne '') {
                # スレッドタイトルの一致判定
                my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[9], '', undef(), '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};

                if (defined($title_match_array_ref)) {
                    # 一致したスレッドタイトルを取り出す
                    my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};

                    # 一致結果配列に追加し、ユニーク化を行う
                    @match_suppress_thread_creation = (
                        [uniq(@{$match_suppress_thread_creation[0]}, @title_match_array)], # 一致スレッドタイトル
                        [uniq(@{$match_suppress_thread_creation[1]}, '**')]                # 一致レス内容  (全てのレス内容に一致のため、**を追加)
                    );

                    # 行設定一致フラグを立てる
                    $match_flag ||= 1;
                }
            }
        }

        # 自動書き込み禁止機能(スレッドタイトル)
        # 判定項目: スレッドタイトル
        #  (新規スレッド作成時のみ判定を行う)
        if ($new_thread_flag && $settings[13] ne '') {
            # スレッドタイトルの一致判定
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[13]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref)) {
                # 一致したスレッドタイトルを取り出す
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};

                # 一致結果配列に追加し、ユニーク化を行う
                @match_title = uniq(@match_title, @title_match_array);

                # 行設定一致フラグを立てる
                $match_flag ||= 1;
            }
        }

        # 自動書き込み禁止機能(レス)
        # 判定項目: スレッドタイトル(一致時先頭@ 付加), レス内容, 文字数除外
        if ($settings[15] ne '' && $settings[16] ne '') {
            # スレッドタイトル・レス内容の一致判定
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[15], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[16]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref) && defined($res_match_array_ref)) {
                # 一致したスレッドタイトル・レスを取り出す
                my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # 対象レス列出力用に隣接AND条件を結合した一致レス部分を取り出す
                my @res_concat_match_array = map { ${$_}[1] } @{${$res_match_array_ref}[0]};

                # 一致結果配列に追加し、ユニーク化を行う
                @match_res = (
                    [uniq(@{$match_res[0]}, @title_match_array)],       # 一致スレッドタイトル
                    [uniq(@{$match_res[1]}, @res_match_array)],         # 一致レス内容
                    [uniq(@{$match_res[2]}, @res_concat_match_array)]   # 対象レス内容
                );

                # 文字数除外指定がある場合は設定値配列に追加してユニーク化を行い、昇順ソートする
                if ($settings[17] ne '') {
                    @valid_exempt_res_length_settings = uniq(@valid_exempt_res_length_settings, int($settings[17]));
                }

                # 行設定一致フラグを立てる
                $match_flag ||= 1;
            }
        }

        # スレッド作成時のレスの強制自動書き込み禁止機能
        # 判定項目: スレッドタイトル, レス内容, 画像アップ
        # (新規スレッド作成時のみ判定を行う)
        if ($new_thread_flag && $settings[29] ne '' && $settings[30] ne '') {
            # スレッドタイトルとレス内容の一致判定
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[29], '', undef(), '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[30]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            # 画像アップ判定 (指定がある場合のみ)
            my $img_upl;
            if ($settings[31] eq '1' && $upfile_count > 0) {
                $img_upl = 1;
            }

            if (defined($title_match_array_ref) && defined($res_match_array_ref) && ($settings[31] ne '1' || $img_upl)) {
                # 一致したスレッドタイトル・レスを取り出す
                my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # 一致結果配列に追加し、ユニーク化を行う
                @force_res_match_on_thread_create = (
                    [uniq(@{$force_res_match_on_thread_create[0]}, @title_match_array)], # 一致スレッドタイトル
                    [uniq(@{$force_res_match_on_thread_create[1]}, @res_match_array)],   # 一致レス内容
                    $force_res_match_on_thread_create[2] || $img_upl                     # 画像アップ
                );

                # 行設定一致フラグを立てる
                $match_flag ||= 1;
            }
        }

        # スレッドタイトルによるレスの強制自動書き込み禁止機能
        # 判定項目: スレッドタイトル, レス内容
        # (レス時のみ判定を行う)
        if (!$new_thread_flag && $settings[33] ne '' && $settings[34] ne '') {
            # スレッドタイトルとレス内容の一致判定
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[33], '', undef(), '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[34]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref) && defined($res_match_array_ref)) {
                # 一致したスレッドタイトル・レスを取り出す
                my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # 一致結果配列に追加し、ユニーク化を行う
                @force_res_match_on_res = (
                    [uniq(@{$force_res_match_on_res[0]}, @title_match_array)], # 一致スレッドタイトル
                    [uniq(@{$force_res_match_on_res[1]}, @res_match_array)]    # 一致レス内容
                );

                # 行設定一致フラグを立てる
                $match_flag ||= 1;
            }
        }

        # スレッド作成時のスレタイの強制自動書き込み禁止機能
        # 判定項目: スレッドタイトル
        # (新規スレッド作成時のみ判定を行う)
        if ($new_thread_flag && $settings[28] ne '') {
            # スレッドタイトルの一致判定
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[28]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref)) {
                # 一致したスレッドタイトルを取り出す
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};

                # 一致結果配列に追加し、ユニーク化を行う
                @force_title_match_on_thread_create = uniq(@force_title_match_on_thread_create, @title_match_array);

                # 行設定一致フラグを立てる
                $match_flag ||= 1;
            }
        }

        # 行設定のいずれかに一致している場合のみ、
        # 一致ユーザー情報を一致結果配列に追加し、ユニーク化を行う
        if ($match_flag) {
            # 一致ユーザー情報を取得
            my @row_match_host = @{${$validsetting_and_userinfo_matchresult_array_ref}[1]};
            my @row_match_useragent = @{${$validsetting_and_userinfo_matchresult_array_ref}[2]};
            my @row_match_cookiea = @{${$validsetting_and_userinfo_matchresult_array_ref}[3]};
            my @row_match_userid = @{${$validsetting_and_userinfo_matchresult_array_ref}[4]};
            my @row_match_historyid = @{${$validsetting_and_userinfo_matchresult_array_ref}[5]};
            my @row_match_time_range = @{${$validsetting_and_userinfo_matchresult_array_ref}[6]};
            my $row_private_browsing_mode_match_flag = ${$validsetting_and_userinfo_matchresult_array_ref}[7];
            my $match_period_str = ($settings[6] ne '' && $settings[7] ne '' ? $enc_cp932->decode("$settings[6]■$settings[7]") : '');

            # 一致結果配列に追加し、ユニーク化を行う
            @match_host = uniq(@match_host, @row_match_host);
            @match_useragent = uniq(@match_useragent, @row_match_useragent);
            @match_cookiea = uniq(@match_cookiea, @row_match_cookiea);
            @match_userid = uniq(@match_userid, @row_match_userid);
            @match_historyid = uniq(@match_historyid, @row_match_historyid);
            @match_time_range = uniq(@match_time_range, @row_match_time_range);
            @match_period = uniq(@match_period, $match_period_str);

            # プライベートブラウジングモード 一致フラグを必要に応じてTrueにする
            $private_browsing_mode_matched_flag ||= $row_private_browsing_mode_match_flag;
        }
    }

    # 自動書き込み禁止機能(レス) 文字数除外
    # 設定値未満で除外対象外の場合、▼を先頭に付与して追加 (除外判定時にはこの値は除外する)
    my @match_res_length_exempt = map { $_ <= $res_length ? $_ : $under_threshold_char . $_; } @valid_exempt_res_length_settings;

    # init.cgiなどに設定がある自動書き込み禁止機能関連の判定
    # ユーザー情報を取得
    my $time = $self->('TIME');
    my $host = $self->('HOST');
    my $useragent = $self->('USERAGENT');
    my $cookie_a = $self->('COOKIE_A');
    my $user_id = $self->('USER_ID');
    my $history_id = $self->('HISTORY_ID');
    my $is_private_browsing_mode = $self->('IS_PRIVATE_BROWSING_MODE');

    # 指定したレスNoまでの自動書き込み禁止機能
    # 判定項目: レス番号, スレッドタイトル, レス1の除外単語, レス文字数除外, レス内容, ホストとUserAgent, CookieA or 登録ID or 書込ID, 時間範囲指定
    # (レス時のみ判定を行う)
    my @match_up_to_res = (0, [], []);
    my @match_up_to_res_res_length_exempt;
    if (!$new_thread_flag) {
        # 設定取り出し
        my @up_to_res_number_setting = @{$self->('UP_TO_RES_NUMBER_SETTING_ARRAY_REF')};

        # 判定ループ
        foreach my $setting_set_str (@up_to_res_number_setting) {
            # 設定値分割
            my @setting_set_array = @{ $mu->number_of_elements_fixed_split($setting_set_str, 10, Matcher::Utils::UTF8_FLAG_FORCE_ON) };
            if (scalar(@setting_set_array) != 10) {
                # 設定が10項目ではない時はスキップ
                next;
            }

            # 制限単語未設定時スキップ
            if ($setting_set_array[3] eq '') {
                next;
            }

            # レス番号が範囲外のときはスキップ
            if (int($setting_set_array[0]) < $new_res_no) {
                next;
            }

            # プライベートモード判定
            my $in_set_private_browsing_mode_match_flg = 0; # 設定セット中プライベートブラウジングモード一致フラグ
            if ($setting_set_array[7] eq '1') {
                # プライベートモードを対象とする設定の場合に、
                # プライベートモードであればフラグをセットし、そうでなければセットをスキップ
                if ($is_private_browsing_mode) {
                    $in_set_private_browsing_mode_match_flg = 1;
                } else {
                    next;
                }
            }

            # レス1の除外単語判定
            if ($setting_set_array[2] ne ''
                && defined($mu->universal_match([$first_res], [$setting_set_array[2]], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
                # レス1の除外単語に合致した場合はセットをスキップ
                next;
            }

            # スレッド名一致判定
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $setting_set_array[1], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (!defined($title_match_array_ref)) {
                # 対象スレッド名に合致しない場合(否定条件では合致した場合)にセットをスキップ
                next;
            }

            # レス内容一致判定
            my $res_match_array_ref = $mu->universal_match([$res], [$setting_set_array[3]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (!defined($res_match_array_ref)) {
                # 制限単語と一致しなかった場合はセットをスキップ
                next;
            }

            # ホストとUserAgent・CookieA or 登録ID or 書込ID・時間範囲指定の設定文字列について、「-」を空に置き換え
            foreach my $i (5, 6, 8) {
                $setting_set_array[$i] =~ s/^-$//;
            }

            # ホストとUserAgentの一致判定
            my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;
            my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[5], ['**', '**'], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (defined($host_useragent_match_array_ref)) {
                $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
            }

            # CookieA or 登録ID or 書込IDの一致判定
            my @cookiea_userid_historyid_match_array = ([], [], []);
            if ($setting_set_array[6] ne '') {
                my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $setting_set_array[6], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($cookiea_userid_historyid_match_array_ref)) {
                    @cookiea_userid_historyid_match_array = @{$cookiea_userid_historyid_match_array_ref};
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }
            }

            # 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」の
            # どちらかで一致していないときは、セットをスキップ
            if ($host_useragent_or_cookiea_userid_historyid_matched_flg == 0) {
                next;
            }

            # 時間範囲指定の一致判定
            my @time_range_match_array;
            if ($setting_set_array[8] ne '') {
                if ($mu->is_in_time_range($setting_set_array[8])) {
                    @time_range_match_array = ($setting_set_array[7]);
                } else {
                    # 時間範囲指定があり、合致しないときはセットをスキップ
                    next;
                }
            }

            # 一致したスレッド名・レスを取り出す
            my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
            my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

            # 一致結果配列に追加して、ユニーク化する
            @match_up_to_res = (
                $match_up_to_res[0] + 1,                            # 一致数カウンター
                [uniq(@{$match_up_to_res[1]}, @title_match_array)], # 一致スレッドタイトル
                [uniq(@{$match_up_to_res[2]}, @res_match_array)]    # 一致レス内容
            );
            @match_host = uniq(@match_host, @{${$host_useragent_match_array_ref}[0]}); # 一致ホスト
            @match_useragent = uniq(@match_useragent, @{${$host_useragent_match_array_ref}[1]}); # 一致UserAgent
            @match_cookiea = uniq(@match_cookiea, @{$cookiea_userid_historyid_match_array[0]}); # 一致CookieA
            @match_userid = uniq(@match_userid, @{$cookiea_userid_historyid_match_array[1]}); # 一致登録ID
            @match_historyid = uniq(@match_historyid, @{$cookiea_userid_historyid_match_array[2]}); # 一致書込ID
            @match_time_range = uniq(@match_time_range, @time_range_match_array); # 一致時間範囲

            # レス文字数除外
            if ($setting_set_array[4] ne '') {
                my $exempt_res_length = int($setting_set_array[4]);
                if ($exempt_res_length <= $res_length) {
                    @match_up_to_res_res_length_exempt = uniq(@match_up_to_res_res_length_exempt, $exempt_res_length);
                } else {
                    # 設定値未満で除外対象外の場合、▼を先頭に付与して追加 (除外判定時にはこの値は除外する)
                    @match_up_to_res_res_length_exempt = uniq(@match_up_to_res_res_length_exempt, $under_threshold_char . $exempt_res_length);
                }
            }

            # プライベートブラウジングモード 一致フラグを必要に応じてTrueにする
            $private_browsing_mode_matched_flag ||= $in_set_private_browsing_mode_match_flg;
        }
    }

    # スレッドNo/スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能の一致フラグ
    my $thread_num_or_name_target_prohibit_flag;

    # スレッドNoを自動書き込み禁止機能のレス部分相当で動作する機能
    # 判定項目: レス内容
    # (「自動書き込み禁止機能(レス)」と同じ出力結果となる)
    my @thread_number_res_target = @{$self->('THREAD_NUMBER_RES_TARGET_ARRAY_REF')};
    if (scalar(@thread_number_res_target) > 0) {
        # 一致判定
        my @thread_number_res_target_hold_hours = @{$self->('THREAD_NUMBER_RES_TARGET_HOLD_HOURS_ARRAY_REF')};
        foreach my $target_hash_ref (@thread_number_res_target) {
            # ハッシュリファレンスではない場合はスキップ
            if (ref($target_hash_ref) ne 'HASH') {
                next;
            }
            my %target_hash = %{$target_hash_ref};

            # 必須キーが無い、もしくは、設定時間を経過した設定はスキップ
            if (!exists($target_hash{thread_number})
                || !exists($target_hash{time})
                || !exists($target_hash{type}) || $target_hash{type} < 0 || $target_hash{type} > 6
                || ($target_hash{type} >= 1
                    && ($target_hash{time} + $thread_number_res_target_hold_hours[$target_hash{type}] * 3600) < $time
                )
            ) {
                next;
            }

            # レス内容の一致判定
            if (!defined($mu->universal_match(([$res], ["no=$target_hash{thread_number}"], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)))) {
                next;
            }

            # 結果出力用に整形して、一致結果配列に追加
            # (一致結果として出力する内容は固定のため、配列として予め用意する)
            my @title_match_array = ('@ **');
            my @res_match_array = ("no=$target_hash{thread_number}");
            my @res_concat_match_array = ("no=$target_hash{thread_number}");
            my @host_match_array = ('**');
            my @useragent_match_array = ('**');

            # 一致結果配列に追加し、ユニーク化を行う
            @match_res = (
                [uniq(@{$match_res[0]}, @title_match_array)],      # 一致スレッドタイトル
                [uniq(@{$match_res[1]}, @res_match_array)],        # 一致レス内容
                [uniq(@{$match_res[2]}, @res_concat_match_array)]  # 対象レス内容
            );
            @match_host = uniq(@match_host, @host_match_array);
            @match_useragent = uniq(@match_useragent, @useragent_match_array);

            # フラグを立てる
            $thread_num_or_name_target_prohibit_flag ||= 1;
        }
    }

    # スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能
    # 判定項目: スレッドタイトル, レス内容
    # (「自動書き込み禁止機能(レス)」と同じ出力結果となる)
    my @thread_title_res_target = @{$self->('THREAD_TITLE_RES_TARGET_ARRAY_REF')};
    if (scalar(@thread_title_res_target) > 0) {
        # 制限単語を内部文字列に変換
        # (最初の要素は、後にindexを使用して処理するためのダミー要素とする)
        my @decoded_restrict_keyword_array = (
            undef,
            map { $enc_cp932->decode($_) } @{$self->('THREAD_TITLE_RES_TARGET_RESTRICT_KEYWORD_ARRAY_REF')}
        );

        # 制限除外単語を内部文字列に変換
        # (最初の要素は、後にindexを使用して処理するためのダミー要素とする)
        my @decoded_restrict_exempt_keyword_array = (
            undef,
            map { $enc_cp932->decode($_) } @{$self->('THREAD_TITLE_RES_TARGET_RESTRICT_EXEMPT_KEYWORD_ARRAY_REF')}
        );

        # 制限時間配列を取得
        # (最初の要素は、後にindexを使用して処理するためのダミー要素とする)
        my @target_hold_hour = (undef, @{$self->('THREAD_TITLE_RES_TARGET_RESTRICT_HOLD_HOUR_ARRAY_REF')});

        # 制限設定ハッシュから制限対象かどうか判定する
        foreach my $target_hash_ref (@thread_title_res_target) {
            # ハッシュリファレンスではない場合はスキップ
            if (ref($target_hash_ref) ne 'HASH') {
                next;
            }
            my %target_hash = %{$target_hash_ref};

            # word_typeが記録されていない場合は、制限単語1とみなす
            if (!exists($target_hash{word_type})) {
                $target_hash{word_type} = 1;
            }

            # 異常設定値、もしくは、設定時間を経過した設定はスキップ
            if (!exists($target_hash{thread_title})
                || !exists($target_hash{type}) || $target_hash{type} < 0 || $target_hash{type} > 6
                || !exists($target_hash{time}) || !defined($target_hash{time})
                || !exists($target_hash{word_type}) || $target_hash{word_type} < 1 || $target_hash{word_type} > 20
                || ($target_hash{type} != 0 && ($target_hash{time} + $target_hold_hour[$target_hash{type}] * 3600) < $time)
            ) {
                next;
            }

            # スレッドタイトルの一致判定・一致スレッドタイトルの取り出し
            my $title_match_array_ref = $mu->universal_match([$title], [$target_hash{thread_title}], ['@ '], ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (!defined($title_match_array_ref)) {
                next;
            }
            my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};

            # レス内容の通常一致判定
            my $decoded_restrict_keyword = $decoded_restrict_keyword_array[$target_hash{word_type}]; # word_typeより一致判定を行う制限単語を決定
            my $res_match_array_ref = $mu->universal_match([$res], [$decoded_restrict_keyword], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (defined($res_match_array_ref)) {
                # 一致レスと、対象レス列出力用に隣接AND条件を結合した一致レス部分を取り出す
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};
                my @res_concat_match_array = map { ${$_}[1] } @{${$res_match_array_ref}[0]};

                # 一致結果として出力する一部の項目の内容は固定のため、配列を予め用意する
                my @host_match_array = ('**');
                my @useragent_match_array = ('**');

                # 一致結果配列に追加し、ユニーク化を行う
                @match_res = (
                    [uniq(@{$match_res[0]}, @title_match_array)],      # 一致スレッドタイトル
                    [uniq(@{$match_res[1]}, @res_match_array)],        # 一致レス内容
                    [uniq(@{$match_res[2]}, @res_concat_match_array)]  # 対象レス内容
                );
                @match_host = uniq(@match_host, @host_match_array);
                @match_useragent = uniq(@match_useragent, @useragent_match_array);

                # フラグを立てる
                $thread_num_or_name_target_prohibit_flag ||= 1;
            }

            # レス内容の除外一致判定
            my $decoded_restrict_exempt_keyword = $decoded_restrict_exempt_keyword_array[$target_hash{word_type}]; # word_typeより一致判定を行う除外単語を決定
            my $exempt_res_match_array_ref = $mu->universal_match([$res], [$decoded_restrict_exempt_keyword], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (defined($exempt_res_match_array_ref)) {
                # レス内容が除外一致している時は、
                # 自動書き込み禁止機能のスレッドタイトルによるレスの除外機能の一致として処理

                # 除外一致レスを取り出す
                my @exempt_res_match_array = map { ${$_}[0] } @{${$exempt_res_match_array_ref}[0]};

                # 自動書き込み禁止機能のスレッドタイトルによるレスの除外機能の
                # 一致結果配列に追加
                push(@{$match_res_exempt_on_res[0]}, @title_match_array);      # 一致スレッドタイトル
                push(@{$match_res_exempt_on_res[1]}, @exempt_res_match_array); # 一致レス内容
            }
        }
    }

    # 複数回投稿時の自動書き込み禁止機能
    # (レス時のみ判定を行う)
    my $multiple_submissions_redirect_flag;
    my @match_multiple_submissions = ();
    if (!$new_thread_flag) {
        # ユーザーカウントログ追加判定
        # 判定項目: スレッドタイトル, レス1の除外単語, レス内容, ホストとUserAgent, CookieA or 登録ID or 書込ID, プライベートモード, 時間範囲指定
        my @multiple_submissions_setting = @{$self->('MULTIPLE_SUBMISSIONS_SETTING_ARRAY_REF')};
        foreach my $setting_str (@multiple_submissions_setting) {
            # 設定値分割
            my @setting_set_array = @{ $mu->number_of_elements_fixed_split($setting_str, 9, Matcher::Utils::UTF8_FLAG_FORCE_ON) };
            if (scalar(@setting_set_array) != 9
                || $setting_set_array[0] eq $disable_setting_char
                || $setting_set_array[1] eq ''
                || $setting_set_array[3] eq ''
            ) {
                # 設定が9項目ではない、無効列に▼、スレッドタイトル or 制限単語が未設定時はセットをスキップ
                next;
            }

            # ホストとUserAgent・CookieA or 登録ID or 書込ID・プライベートモード・時間範囲指定について、
            # 「-」を空文字列に置き換える
            foreach my $i (4 .. 7) {
                $setting_set_array[$i] =~ s/^-$//;
            }

            # プライベートモード判定
            my $in_set_private_browsing_mode_match_flg = 0; # 設定セット中プライベートブラウジングモード一致フラグ
            if ($setting_set_array[6] eq '1') {
                # プライベートモードを対象とする設定の場合に、
                # プライベートモードであればフラグをセットし、そうでなければセットをスキップ
                if ($is_private_browsing_mode) {
                    $in_set_private_browsing_mode_match_flg = 1;
                } else {
                    next;
                }
            }

            # レス1の除外単語判定
            if ($setting_set_array[2] ne ''
                && defined($mu->universal_match([$first_res], [$setting_set_array[2]], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
                # レス1の除外単語に合致した場合はセットをスキップ
                next;
            }

            # スレッド名一致判定
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $setting_set_array[1], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (!defined($title_match_array_ref)) {
                # 対象スレッド名に合致しない場合(否定条件では合致した場合)にセットをスキップ
                next;
            }

            # レス内容一致判定
            my $res_match_array_ref = $mu->universal_match([$res], [$setting_set_array[3]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (!defined($res_match_array_ref)) {
                # 制限単語と一致しなかった場合はセットをスキップ
                next;
            }

            # 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」のいずれかで一致したかどうかのフラグ
            my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;

            # ホストとUserAgentの一致判定
            my @host_useragent_match_array = ([], []);
            if ($setting_set_array[4] ne '') {
                my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[4], ['**', '**'], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($host_useragent_match_array_ref)) {
                    @host_useragent_match_array = @{$host_useragent_match_array_ref};
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }
            }

            # CookieA or 登録ID or 書込IDの一致判定
            my @cookiea_userid_historyid_match_array = ([], [], []);
            if ($setting_set_array[5] ne '') {
                my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $setting_set_array[5], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($cookiea_userid_historyid_match_array_ref)) {
                    @cookiea_userid_historyid_match_array = @{$cookiea_userid_historyid_match_array_ref};
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }
            }

            # 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」の
            # どちらかで一致していないときは、スキップ
            if ($host_useragent_or_cookiea_userid_historyid_matched_flg == 0) {
                next;
            }

            # 時間範囲指定の一致判定
            my @match_time_range_array;
            if ($setting_set_array[7] ne '') {
                if ($mu->is_in_time_range($setting_set_array[7])) {
                    @match_time_range_array = ($setting_set_array[7]);
                } else {
                    next;
                }
            }

            # 一致したレスを取り出す
            my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

            # 一致結果配列に追加して、ユニーク化する
            @match_multiple_submissions = uniq(@match_multiple_submissions, @res_match_array); # 一致レス
            @match_host = uniq(@match_host, @{$host_useragent_match_array[0]}); # 一致ホスト
            @match_useragent = uniq(@match_useragent, @{$host_useragent_match_array[1]}); # 一致UserAgent
            @match_cookiea = uniq(@match_cookiea, @{$cookiea_userid_historyid_match_array[0]}); # 一致CookieA
            @match_userid = uniq(@match_userid, @{$cookiea_userid_historyid_match_array[1]}); # 一致登録ID
            @match_historyid = uniq(@match_historyid, @{$cookiea_userid_historyid_match_array[2]}); # 一致書込ID
            @match_time_range = uniq(@match_time_range, @match_time_range_array); # 一致時間範囲

            # プライベートブラウジングモード 一致フラグを必要に応じてTrueにする
            $private_browsing_mode_matched_flag ||= $in_set_private_browsing_mode_match_flg;
        }

        # リダイレクト判定と、現在ユーザー情報のユーザーカウントログ配列への追加
        # (ユーザーカウントログ追加対象の場合のみ)
        if (scalar(@match_multiple_submissions) > 0) {
            # ユーザーカウントログ配列リファレンスを取得
            my $multiple_submissions_validlog_array_ref = $self->('MULTIPLE_SUBMISSIONS_VALIDLOG_ARRAY_REF');

            # 同一ユーザーの投稿数によるリダイレクト判定
            my $same_user_count = 0;
            foreach my $validlog_array_ref (@{$multiple_submissions_validlog_array_ref}) {
                my ($log_host, $log_cookiea, $log_userid, $log_history_id) = @{$validlog_array_ref};
                if (($log_host ne '' && $log_host eq $host)
                    || ($log_cookiea ne '' && $log_cookiea eq $cookie_a)
                    || ($log_userid ne '' && $log_userid eq $user_id)
                    || ($log_history_id ne '' && $log_history_id eq $history_id)
                ) {
                    $same_user_count++;
                }
            }
            $multiple_submissions_redirect_flag = $same_user_count >= $self->('MULTIPLE_SUBMISSIONS_REDIRECT_THRESHOLD');

            # ユーザーカウントログ配列に現在ユーザー情報を追加
            if ($self->('MULTIPLE_SUBMISSIONS_LOG_RECORD_HOST_FLAG')) {
                push(@{$multiple_submissions_validlog_array_ref}, [$host, $cookie_a, $user_id, $history_id, $time]);
            } else {
                push(@{$multiple_submissions_validlog_array_ref}, ['', $cookie_a, $user_id, $history_id, $time]);
            }
        }
    }

    # 古スレageの自動書き込み禁止機能
    # (ageのレス時のみ判定を行う)
    my $old_thread_age_redirect_flag;
    my $match_old_thread_age_flag;
    if (!$new_thread_flag && $age_flag) {
        # 直前レスのタイムスタンプを取り出す
        my $last_res_timestamp = ${${$log_array_ref}[$#{$log_array_ref}]}[11];

        # 古スレageユーザーカウントログ追加判定
        # 判定項目: スレッドタイトル, 直前レスが何時間前, ホストとUserAgent, CookieA or 登録ID or 書込ID, プライベートモード, 時間範囲指定
        my @old_thread_age_setting = @{$self->('OLD_THREAD_AGE_SETTING_ARRAY_REF')};
        foreach my $setting_str (@old_thread_age_setting) {
            # 設定値分割
            my @setting_set_array = @{ $mu->number_of_elements_fixed_split($setting_str, 8, Matcher::Utils::UTF8_FLAG_FORCE_ON) };
            if (scalar(@setting_set_array) != 8
                || $setting_set_array[0] eq $disable_setting_char
                || $setting_set_array[1] eq ''
                || $setting_set_array[2] eq ''
            ) {
                # 設定が8項目ではない、無効列に▼、スレッドタイトル・直前レスが何時間前が未設定時はセットをスキップ
                next;
            }

            # ホストとUserAgent・CookieA or 登録ID or 書込ID・プライベートモード・時間範囲指定について、
            # 「-」を空文字列に置き換える
            foreach my $i (3 .. 6) {
                $setting_set_array[$i] =~ s/^-$//;
            }

            # プライベートモード判定
            my $in_set_private_browsing_mode_match_flg = 0; # 設定セット中プライベートブラウジングモード一致フラグ
            if ($setting_set_array[5] eq '1') {
                # プライベートモードを対象とする設定の場合に、
                # プライベートモードであればフラグをセットし、そうでなければセットをスキップ
                if ($is_private_browsing_mode) {
                    $in_set_private_browsing_mode_match_flg = 1;
                } else {
                    next;
                }
            }

            # 「直前レスが何時間前」判定
            if (($time - $setting_set_array[2] * 3600) < $last_res_timestamp) {
                # 「直前レスが何時間前」に達していない場合はセットをスキップ
                next;
            }

            # スレッド名一致判定
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $setting_set_array[1], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (!defined($title_match_array_ref)) {
                # 対象スレッド名に合致しない場合(否定条件では合致した場合)にセットをスキップ
                next;
            }

            # 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」のいずれかで一致したかどうかのフラグ
            my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;

            # ホストとUserAgentの一致判定
            my @host_useragent_match_array = ([], []);
            if ($setting_set_array[3] ne '') {
                my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[3], ['**', '**'], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($host_useragent_match_array_ref)) {
                    @host_useragent_match_array = @{$host_useragent_match_array_ref};
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }
            }

            # CookieA or 登録ID or 書込IDの一致判定
            my @cookiea_userid_historyid_match_array = ([], [], []);
            if ($setting_set_array[4] ne '') {
                my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $setting_set_array[4], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($cookiea_userid_historyid_match_array_ref)) {
                    @cookiea_userid_historyid_match_array = @{$cookiea_userid_historyid_match_array_ref};
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }
            }

            # 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」の
            # どちらかで一致していないときは、スキップ
            if ($host_useragent_or_cookiea_userid_historyid_matched_flg == 0) {
                next;
            }

            # 時間範囲指定の一致判定
            my @match_time_range_array;
            if ($setting_set_array[6] ne '') {
                if ($mu->is_in_time_range($setting_set_array[6])) {
                    @match_time_range_array = ($setting_set_array[6]);
                } else {
                    next;
                }
            }

            # 一致フラグを立てる
            $match_old_thread_age_flag ||= 1;

            # 一致結果配列に追加して、ユニーク化する
            @match_host = uniq(@match_host, @{$host_useragent_match_array[0]}); # 一致ホスト
            @match_useragent = uniq(@match_useragent, @{$host_useragent_match_array[1]}); # 一致UserAgent
            @match_cookiea = uniq(@match_cookiea, @{$cookiea_userid_historyid_match_array[0]}); # 一致CookieA
            @match_userid = uniq(@match_userid, @{$cookiea_userid_historyid_match_array[1]}); # 一致登録ID
            @match_historyid = uniq(@match_historyid, @{$cookiea_userid_historyid_match_array[2]}); # 一致書込ID
            @match_time_range = uniq(@match_time_range, @match_time_range_array); # 一致時間範囲

            # プライベートブラウジングモード 一致フラグを必要に応じてTrueにする
            $private_browsing_mode_matched_flag ||= $in_set_private_browsing_mode_match_flg;
        }

        # リダイレクト判定と、現在ユーザー情報の古スレageユーザーカウントログ配列への追加
        # (古スレageユーザーカウントログ追加対象の場合のみ)
        if ($match_old_thread_age_flag) {
            # 古スレageユーザーカウントログ配列リファレンスを取得
            my $old_thread_age_validlog_array_ref = $self->('OLD_THREAD_AGE_VALIDLOG_ARRAY_REF');

            # 同一ユーザーの投稿数によるリダイレクト判定
            my $same_user_count = 0;
            foreach my $validlog_array_ref (@{$old_thread_age_validlog_array_ref}) {
                my ($log_host, $log_cookiea, $log_userid, $log_history_id) = @{$validlog_array_ref};
                if (($log_host ne '' && $log_host eq $host)
                    || ($log_cookiea ne '' && $log_cookiea eq $cookie_a)
                    || ($log_userid ne '' && $log_userid eq $user_id)
                    || ($log_history_id ne '' && $log_history_id eq $history_id)
                ) {
                    $same_user_count++;
                }
            }
            $old_thread_age_redirect_flag = $same_user_count >= $self->('OLD_THREAD_AGE_REDIRECT_THRESHOLD');

            # 古スレageユーザーカウントログ配列に現在ユーザー情報を追加
            if ($self->('OLD_THREAD_AGE_LOG_RECORD_HOST_FLAG')) {
                push(@{$old_thread_age_validlog_array_ref}, [$host, $cookie_a, $user_id, $history_id, $time]);
            } else {
                push(@{$old_thread_age_validlog_array_ref}, ['', $cookie_a, $user_id, $history_id, $time]);
            }
        }
    }

    # 画像の自動書き込み禁止機能
    # 判定項目: スレッドタイトル, 変換前/変換後画像のMD5, 一致時ログ出力コメント, ホストとUserAgent, CookieA or 登録ID or 書込ID
    my @match_img_md5 = ([], [], []);
    my @combination_img_md5 = @{$self->('COMBINATION_IMG_MD5_ARRAY_REF')};
    if (scalar(@combination_img_md5) > 0) {
        my @image_md5_concat_one_dimensional_array = map { (grep { $_ ne '' } @{$_}) } @{$image_md5_array_ref_array_ref};
        if (scalar(@image_md5_concat_one_dimensional_array) > 0) {
            foreach my $setting_set_str (@combination_img_md5) {
                # 一致判定実施
                my @setting_set_array = split(/:/, $enc_cp932->decode($setting_set_str), 5);
                if (scalar(@setting_set_array) != 5) {
                    next;
                }

                # スレッドタイトル・ホストとUserAgent・CookieA or 登録ID or 書込IDの設定文字列について、「-」を空に置き換え
                foreach my $i (0, 3, 4) {
                    $setting_set_array[$i] =~ s/^-$//;
                }

                # MD5の一致判定
                my @setting_md5_array = grep { $_ ne '' } split(/,/, $setting_set_array[1]);
                my @md5_match_array = grep {
                    my $setting_md5 = $_;
                    grep { $_ eq $setting_md5 } @image_md5_concat_one_dimensional_array;
                } @setting_md5_array;
                if (scalar(@md5_match_array) == 0) {
                    next;
                }

                # スレッドタイトルの否定一致判定
                my @title_not_match_settings_array;
                if ($setting_set_array[0] ne '') {
                    if (defined($mu->universal_match([$title], [$setting_set_array[0]], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
                        # 否定条件のため、一致してしまった場合はスキップ
                        next;
                    }
                    # 一致しなかった場合は、設定値を保管
                    push(@title_not_match_settings_array, $setting_set_array[0]);
                }

                # ホストとUserAgentの一致判定
                my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;
                my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[3], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($host_useragent_match_array_ref)) {
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }

                # CookieA or 登録ID or 書込IDの一致判定
                my @cookiea_userid_historyid_match_array = ([], [], []);
                if ($setting_set_array[4] ne '') {
                    my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $setting_set_array[4], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                    if (defined($cookiea_userid_historyid_match_array_ref)) {
                        @cookiea_userid_historyid_match_array = @{$cookiea_userid_historyid_match_array_ref};
                        $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                    }
                }

                if ($host_useragent_or_cookiea_userid_historyid_matched_flg == 0) {
                    # 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」の
                    # どちらかで一致していないときは、スキップ
                    next;
                }

                # 一致結果配列に追加し、ユニーク化を行う
                @match_img_md5 = (
                    [uniq(@{$match_img_md5[0]}, @title_not_match_settings_array)], # スレッドタイトル否定条件
                    [uniq(@{$match_img_md5[1]}, @md5_match_array)],                # 一致画像MD5
                    [uniq(@{$match_img_md5[3]}, $setting_set_array[2])]            # 一致時ログ出力コメント
                );
            }
        }
    }

    # レス時に、
    # 自動書き込み禁止機能(名前・レス)、指定したレスNoまでの自動書き込み禁止機能、強制自動書き込み禁止機能以外の
    # 自動書き込み禁止機能に一致したかどうか
    my $other_res_match_on_res_flag =
        !$new_thread_flag
        && ($multiple_submissions_redirect_flag || $old_thread_age_redirect_flag);

    # スレッド作成抑制機能・自動書き込み禁止機能のスレッド作成時のレスの除外機能
    # もしくは
    # 自動書き込み禁止機能のスレッドタイトルによるレスの除外機能(▲を除いた一致数カウント)の
    # 設定値に一致したかどうか
    my $res_exempt_match_flag =
        scalar(@{$match_res_exempt_on_thread_create[0]}) > 0
        || scalar(@{$match_res_exempt_on_res[0]}) - scalar(grep { index($_, $over_threshold_char) >= 0 } @{$match_res_exempt_on_res[2]}) > 0;

    # スレッド作成抑制機能・自動書き込み禁止機能(共にスレッドタイトル部分)の除外機能の
    # 設定値に一致したかどうか
    my $title_exempt_match_flag = scalar(@match_title_exempt_on_thread_create) > 0;

    # 自動書き込み禁止機能(レス) 文字数除外の設定値に一致したかどうか
    # (▼は除外対象外のため、これを除いた一致数をカウントする)
    my $res_length_exempt_match_flag = scalar(grep { index($_, $under_threshold_char) == -1 } @match_res_length_exempt) > 0;

    # 指定したレスNoまでの自動書き込み禁止機能 文字数除外の設定値に一致したかどうか
    # (▼は除外対象外のため、これを除いた一致数をカウントする)
    my $up_to_res_res_length_exempt_match_flag = scalar(grep { index($_, $under_threshold_char) == -1 } @match_up_to_res_res_length_exempt) > 0;

    # スレッド作成抑制機能・自動書き込み禁止機能(共にスレッドタイトル部分)の除外機能の
    # 除外対象かどうか
    my $title_prohibit_exempt_flag =
        scalar(@{$match_name[0]}) == 0
            && (scalar(@{$match_suppress_thread_creation[0]}) > 0 || scalar(@match_title) > 0)
            && $title_exempt_match_flag;

    # スレッド作成抑制機能・自動書き込み禁止機能のスレッド作成時のレスの除外機能の
    # 除外対象かどうか
    my $res_prohibit_exempt_flag =
        scalar(@{$match_name[0]}) == 0
            && (!$title_prohibit_exempt_flag
                || (scalar(@{$match_res[0]}) > 0 && !$res_length_exempt_match_flag)
                || ($match_up_to_res[0] > 0 && !$up_to_res_res_length_exempt_match_flag)
                || $other_res_match_on_res_flag
            )
            && $res_exempt_match_flag;

    # 自動書き込み禁止機能(レス)の文字数除外に合致していたかどうか
    my $res_length_prohibit_exempt_flag =
        scalar(@{$match_name[0]}) == 0
            && scalar(@{$match_suppress_thread_creation[0]}) == 0
            && (scalar(@match_title) == 0 || $title_exempt_match_flag)
            && scalar(@{$match_res[0]}) > 0
            && $res_length_exempt_match_flag;

    # 指定したレスNoまでの自動書き込み禁止機能の文字数除外に合致していたかどうか
    my $up_to_res_res_length_prohibit_exempt_flag =
        scalar(@{$match_name[0]}) == 0
            && $match_up_to_res[0] > 0
            && $up_to_res_res_length_exempt_match_flag;

    # 強制自動書き込み禁止機能で合致したかどうか
    my $force_match_flag =
        scalar(@{$force_res_match_on_thread_create[0]}) > 0
            || scalar(@{$force_res_match_on_res[0]}) > 0
            || scalar(@force_title_match_on_thread_create) > 0;

    # 画像の自動書き込み禁止機能で合致したかどうか
    my $img_md5_match_flag = scalar(@{$match_img_md5[1]}) > 0;

    # ログに含まれるユーザーかどうか
    my $log_exist_user_flag =
        $self->('LOG_EXIST_HOST_FLAG')
            || $self->('LOG_EXIST_COOKIEA_FLAG')
            || $self->('LOG_EXIST_USERID_FLAG')
            || $self->('LOG_EXIST_HISTORYID_FLAG');

    # ログに含まれるのみのユーザーかどうか
    my $log_exist_only_user_flag =
        $log_exist_user_flag
            && scalar(@{$match_name[0]}) == 0
            && scalar(@{$match_suppress_thread_creation[0]}) == 0
            && scalar(@match_title) == 0
            && scalar(@{$match_res[0]}) == 0
            && $match_up_to_res[0] == 0
            && !$other_res_match_on_res_flag
            && !$force_match_flag
            && !$img_md5_match_flag;

    # スレッド作成抑制機能の対象であるかどうか
    my $suppress_thread_creation_flag =
        $new_thread_flag
            && scalar(@{$match_name[0]}) == 0
            && scalar(@{$match_suppress_thread_creation[0]}) > 0
            && !$res_exempt_match_flag
            && !$title_exempt_match_flag
            && !$force_match_flag
            && !$img_md5_match_flag;

    # リダイレクトの対象であるかどうか
    my $redirect_flag =
        scalar(@{$match_name[0]}) > 0
            || (!$suppress_thread_creation_flag
                && (!$res_prohibit_exempt_flag
                    && ((scalar(@match_title) > 0 && !$title_exempt_match_flag)
                        || (scalar(@{$match_res[0]}) > 0 && !$res_length_prohibit_exempt_flag)
                        || ($match_up_to_res[0] > 0 && !$up_to_res_res_length_prohibit_exempt_flag)
                        || $other_res_match_on_res_flag
                    )
                    || $force_match_flag
                    || $img_md5_match_flag
                )
            )
            || $log_exist_user_flag;

    # 書き込み禁止ログ追記対象であるかどうか
    my $log_add_flag =
        $log_exist_user_flag
            || scalar(@{$match_name[0]}) > 0
            || scalar(@{$match_suppress_thread_creation[0]}) > 0
            || scalar(@match_title) > 0
            || scalar(@{$match_res[0]}) > 0
            || $match_up_to_res[0] > 0
            || $other_res_match_on_res_flag
            || $force_match_flag
            || $img_md5_match_flag;

    # 複数回投稿時の自動書き込み禁止機能 ユーザーカウントログ追記対象であるかどうか
    my $multiple_submissions_log_add_flag =
        scalar(@{$match_name[0]}) == 0
            && scalar(@match_multiple_submissions) > 0
            && ((
                    (scalar(@{$match_res[0]}) == 0 || !$res_length_prohibit_exempt_flag)
                    && ($match_up_to_res[0] == 0 || !$up_to_res_res_length_prohibit_exempt_flag)
                    && !$res_exempt_match_flag
                )
                || $force_match_flag
                || $img_md5_match_flag
            );

    # 古スレageの自動書き込み禁止機能 古スレageユーザーカウントログ追記対象であるかどうか
    my $old_thread_age_log_add_flag =
        scalar(@{$match_name[0]}) == 0
            && $match_old_thread_age_flag
            && ((
                    (scalar(@{$match_res[0]}) == 0 || !$res_length_prohibit_exempt_flag)
                    && ($match_up_to_res[0] == 0 || !$up_to_res_res_length_prohibit_exempt_flag)
                    && !$res_exempt_match_flag
                )
                || $force_match_flag
                || $img_md5_match_flag
            );

    # 書き込み禁止ログ追記対象であれば、追記内容を作成
    my $log_add_contents;
    if ($log_add_flag) {
        # Cookie Aが未発行の場合に発行する
        if (!defined($cookie_a)) {
            my UniqueCookie $cookie_a_instance = $self->('COOKIE_A_INSTANCE');
            $cookie_a = $cookie_a_instance->value(1);
            $self->('COOKIE_A', $cookie_a);
        }

        # ログに含まれるのみのユーザーの場合は、一部の出力項目で「-----」を出力
        my $log_only = $log_exist_only_user_flag ? '-----' : '';

        # スレッド作成抑制対象の場合は、一部の出力項目で先頭に「●」を付加する
        my $thread_create_suppress_str = $suppress_thread_creation_flag ? '●' : '';

        # 書き込み内容と一致した禁止対象文字列などをログ出力項目に追加
        my ($add_name, $add_title, $add_res) = ($name, $category_removed_title, $res);
        my $add_match_name = log_join($log_only, @{$match_name[1]});
        my $add_match_suppress_thread_creation_title = log_join($log_only, @{$match_suppress_thread_creation[0]});
        my $add_match_suppress_thread_creation_res = log_join($log_only, @{$match_suppress_thread_creation[1]});
        my $add_match_title = log_join(
            $log_only,
            @{$match_name[0]}, @match_title, @{$match_res[0]}, @{$match_up_to_res[1]}, @{$match_img_md5[0]}
        );
        my $add_match_res = log_join($log_only, @{$match_res[1]});
        my $add_match_concat_res = log_join($log_only, @{$match_res[2]});
        my $add_match_up_to_res = log_join($log_only, @{$match_up_to_res[2]});
        my $add_match_multiple_submissions = log_join($log_only, @match_multiple_submissions);
        my $add_old_thread_age = $log_only || ($old_thread_age_redirect_flag ? '●' : '');
        my $add_force_title_match_on_thread_create = log_join($log_only, @force_title_match_on_thread_create);
        my $add_force_res_match_on_thread_create_title = log_join($log_only, @{$force_res_match_on_thread_create[0]});
        my $add_force_res_match_on_thread_create_res = log_join($log_only, @{$force_res_match_on_thread_create[1]});
        my $add_force_res_match_on_res_title = log_join($log_only, @{$force_res_match_on_res[0]});
        my $add_force_res_match_on_res_res = log_join($log_only, @{$force_res_match_on_res[1]});
        my $add_match_host = log_join(undef, @match_host);
        my $add_match_useragent = log_join(undef, @match_useragent);
        my $add_match_cookiea = log_join(undef, @match_cookiea);
        my $add_match_userid = log_join(undef, @match_userid);
        my $add_match_historyid =log_join(undef, @match_historyid);
        my $add_match_img_md5 = log_join(undef, @{$match_img_md5[1]});
        my $add_match_img_md5_comment = log_join(undef, @{$match_img_md5[2]});
        my $add_match_time_range = log_join(undef, @match_time_range);
        my $add_match_period = log_join(undef, @match_period);
        my $add_res_exempt_on_thread_create_match_title = log_join($log_only, @{$match_res_exempt_on_thread_create[0]});
        my $add_res_exempt_on_thread_create_match_res = log_join($log_only, @{$match_res_exempt_on_thread_create[1]});
        my $add_match_title_exempt_on_thread_create = log_join($log_only, @match_title_exempt_on_thread_create);
        my $add_res_exempt_on_res_match_title = log_join($log_only, uniq(@{$match_res_exempt_on_res[0]}));
        my $add_res_exempt_on_res_match_res = log_join($log_only, uniq(@{$match_res_exempt_on_res[1]}));
        my $add_res_exempt_on_res_match_up_to_res_num_exempt = log_join($log_only, uniq(@{$match_res_exempt_on_res[2]}));
        my $add_match_res_length_exempt = log_join($log_only, @match_res_length_exempt);
        my $add_match_up_to_res_res_length_exempt = log_join($log_only, @match_up_to_res_res_length_exempt);
        my $add_img_upl_match_flag = $log_only || $force_res_match_on_thread_create[2];

        # 名前,スレッドタイトル,レス内容の半角カンマを取り除く
        $add_name =~ tr/,//d;
        $add_title =~ tr/,//d;
        $add_res =~ tr/,//d;

        # ステータス列
        my $status;
        if ($log_exist_only_user_flag) {
            # ログに含まれるのみのユーザーの場合は「-」を出力
            $status = '-';
        } elsif ($new_thread_flag) {
            $status = $thread_create_suppress_str . '作成';
        } else {
            $status = 'レ';
        }
        if ($thread_num_or_name_target_prohibit_flag) {
            # スレッドNo/スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能で
            # 一致した場合に、ステータス列末尾に「★」を出力する
            $status .= '★';
        }

        # 日付列
        my $date = $self->('DATE');

        # CookieA発行列
        my $cookie_a_issuing_str = '';
        if ($self->('COOKIE_A_ISSUING_FLAG')) {
            $cookie_a_issuing_str = '生成';
        }

        # スレタイ除外列
        my $title_exempt = '';
        if ($title_prohibit_exempt_flag) {
            $title_exempt = '除外';
        }

        # 除外列
        my $exempt = '';
        if ((!$other_res_match_on_res_flag
                && (($res_length_prohibit_exempt_flag && $up_to_res_res_length_prohibit_exempt_flag)
                    || ($res_length_prohibit_exempt_flag && $match_up_to_res[0] == 0)
                    || ($up_to_res_res_length_prohibit_exempt_flag && scalar(@{$match_res[0]}) == 0)
                )
            )
            || $res_prohibit_exempt_flag
        ) {
            $exempt = '除外';
        }

        # 強制列
        my $force_prohibit = '';
        if ($force_match_flag) {
            $force_prohibit .= '●1';
        }
        if ($img_md5_match_flag) {
            $force_prohibit .= '●p';
        }

        # URL列 (レス時か、除外によるスレッド作成時のみ、@auto_post_prohibit_log_concat_urlとスレッドNoを結合して出力)
        my $url = '';
        if (!$new_thread_flag
            || (!$suppress_thread_creation_flag && !$redirect_flag && ($title_exempt ne '' || $exempt ne ''))
        ) {
            $url = $self->('LOG_CONCAT_URL') . $thread_no;
        }

        # プライベートモード/プライベートモード判定列
        my $private_browsing_mode_str = $is_private_browsing_mode ? 'プ' : '';
        my $private_browsing_mode_matched_str = $private_browsing_mode_matched_flag ? 'プ' : '';

        # 文字数列
        my $res_length_str = $log_only || $res_length;

        # 画像枚数列
        my $upfile_count_str = $upfile_count > 0 ? "${upfile_count}枚" : '';

        # 追加するログ行を作成
        $log_add_contents = join(',',
            map { Encode::is_utf8($_) ? $_ : $enc_cp932->decode($_) } (
                $date, # 日時
                $cookie_a_issuing_str, # CookieA発行
                $private_browsing_mode_matched_str, # プライベート判定
                $add_match_time_range, # 一致時間
                $add_match_period, # 期間指定
                $status, # ステータス
                $title_exempt, # スレタイ除外
                $exempt, # 除外
                $force_prohibit, # 強制
                $url, # URL
                $category, # カテゴリ
                '■',
                $add_match_title, # 一致スレタイ
                $add_match_title_exempt_on_thread_create, # スレタイ部分の除外
                $add_match_suppress_thread_creation_title, # 一致スレタイ(抑制)
                $add_match_suppress_thread_creation_res, # 一致レス(抑制)
                '■',
                $add_match_name, # 一致名前
                '■',
                $res_length_str, # 文字数
                $add_match_concat_res, # 対象のレス
                $add_match_res, # 一致レス
                $add_match_res_length_exempt, # 文字数除外 (自動書き込み禁止機能(レス))
                $add_match_up_to_res, # 指定レス番までの一致レス
                $add_match_up_to_res_res_length_exempt, # 文字数除外 (指定したレスNoまでの自動書き込み禁止機能)
                $add_match_multiple_submissions, # 複数回レス
                $add_old_thread_age, # 古スレage
                '■',
                $add_res_exempt_on_thread_create_match_title, # スレ作成時のスレタイによるレスの除外（スレ）
                $add_res_exempt_on_thread_create_match_res, # スレ作成時のスレタイによるレスの除外（レス）
                $add_res_exempt_on_res_match_title, # スレタイによるレスの除外(スレ)
                $add_res_exempt_on_res_match_res, # スレタイによるレスの除外(レス)
                $add_res_exempt_on_res_match_up_to_res_num_exempt, # 指定レスまで除外
                '■',
                $add_force_title_match_on_thread_create, # スレ作成時のスレタイ強制一致
                $add_force_res_match_on_thread_create_title, # スレ作成時の強制一致レス(スレ)
                $add_force_res_match_on_thread_create_res, # スレ作成時の強制一致レス(レス)
                $add_force_res_match_on_res_title, # スレタイによる強制一致レス(スレ)
                $add_force_res_match_on_res_res, # スレタイによる強制一致レス(レス)
                $add_img_upl_match_flag, # 画像アップ
                '■',
                $add_match_cookiea, # 一致CookieA
                $add_match_userid, # 一致登録ID
                $add_match_historyid, # 一致書込ID
                $add_match_host, # 一致ホスト
                $add_match_useragent, # 一致UserAgent
                $add_match_img_md5, # 一致MD5
                $add_match_img_md5_comment, # 一致画像コメント
                '■',
                $add_title, # スレタイ
                $add_name, # 名前
                $add_res, # レス内容
                $upfile_count_str, # 画像枚数
                $private_browsing_mode_str, # プライベート
                defined($cookie_a) && $cookie_a ne '' ? $thread_create_suppress_str . $cookie_a : '', # CookieA
                defined($user_id) && $user_id ne '' ? $thread_create_suppress_str . $user_id : '', # 登録ID
                defined($history_id) && $history_id ne '' ? $thread_create_suppress_str . $history_id : '', # 書込ID
                $host ne '' ? $thread_create_suppress_str . $host : '', # ホスト
                $useragent, # UserAgent
                $time, # タイムスタンプ
                $idcrypt  # ID
            )
        ) . "\n";
    }

    # 必要に応じてログファイルに書き込む
    write_log($self, $log_add_contents);

    # 複数回投稿時の自動書き込み禁止機能 ユーザーカウントログに書き込む
    if ($multiple_submissions_log_add_flag) {
        write_multiple_submissions_log($self);
    }

    # 古スレageの自動書き込み禁止機能 古スレageユーザーカウントログに書き込む
    if ($old_thread_age_log_add_flag) {
        write_old_thread_age_log($self);
    }

    # 判定結果を返す
    my $result = RESULT_ALL_PASSED;
    if ($suppress_thread_creation_flag) {
        # スレッド作成抑制対象
        $result |= RESULT_THREAD_CREATE_SUPPRESS_REQUIRED;
    }
    if ($redirect_flag) {
        # リダイレクト対象
        $result |= RESULT_REDIRECT_REQUIRED;
    }
    return $result;
}

# ログ出力項目結合サブルーチン定義
sub log_join {
    my ($only_log_matched_str, @concat_items) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }

    if (defined($only_log_matched_str) && $only_log_matched_str ne '') {
        return $only_log_matched_str;
    } else {
        my $ret_str = join(';', grep { defined($_) && $_ ne '' } @concat_items);
        $ret_str =~ tr/,//d;
        return $ret_str;
    }
}

# ログ書き込みサブルーチン定義
sub write_log {
    my ($self, $log_add_contents) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }
    arg_check(2, ['AutoPostProhibit', undef], @_);

    # ログファイルハンドラー取得
    my $log_fh = $self->('LOG_FH');
    my $no_delete_log_fh = $self->('NO_DELETE_LOG_FH');

    # ヘッダー定義
    my $header_str = join(',', @log_header) . "\n${log_second_header_row}\n";

    # 消去ログ書き込み
    if ($self->('NEW_LOG_FLAG') || $self->('READ_SKIP_FLAG') || defined($log_add_contents)) {
        my $read_log_contents = $self->('READ_LOG_CONTENTS');
        seek($log_fh, 0, 0);
        if (defined($log_add_contents)) {
            print $log_fh $header_str . $read_log_contents . $log_add_contents;
        } else {
            print $log_fh $header_str . $read_log_contents;
        }
        truncate($log_fh, tell($log_fh));
    }

    # 累積ログ書き込み
    # (累積ログ新規作成時・ファイルサイズが0の時は、予めヘッダーを追加)
    if ($self->('NEW_NO_DELETE_LOG_FLAG')) {
        print $no_delete_log_fh $header_str;
    }
    if (defined($log_add_contents)) {
        seek($no_delete_log_fh, 0, 2);
        print $no_delete_log_fh $log_add_contents;
    }

    # ログファイルクローズ
    close($log_fh);
    close($no_delete_log_fh);
};

# 複数回投稿時の自動書き込み禁止機能 ユーザーカウントログ書き込みサブルーチン定義
sub write_multiple_submissions_log {
    my ($self) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }
    arg_check(1, ['AutoPostProhibit'], @_);

    # ログファイルハンドル取得
    my $multiple_submissions_count_log_fh = $self->('MULTIPLE_SUBMISSIONS_COUNT_LOG_FH');

    # 書き込み
    seek($multiple_submissions_count_log_fh, 0, 0);
    foreach my $validlog_array_ref (@{$self->('MULTIPLE_SUBMISSIONS_VALIDLOG_ARRAY_REF')}) {
        print $multiple_submissions_count_log_fh join($multiple_submissions_count_log_delimiter, @{$validlog_array_ref}) . "\n";
    }
    truncate($multiple_submissions_count_log_fh, tell($multiple_submissions_count_log_fh));

    # クローズ
    close($multiple_submissions_count_log_fh);
}

# 古スレageの自動書き込み禁止機能 古スレageユーザーカウントログ書き込みサブルーチン定義
sub write_old_thread_age_log {
    my ($self) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }
    arg_check(1, ['AutoPostProhibit'], @_);

    # ログファイルハンドル取得
    my $old_thread_age_count_log_fh = $self->('OLD_THREAD_AGE_COUNT_LOG_FH');

    # 書き込み
    seek($old_thread_age_count_log_fh, 0, 0);
    foreach my $validlog_array_ref (@{$self->('OLD_THREAD_AGE_VALIDLOG_ARRAY_REF')}) {
        print $old_thread_age_count_log_fh join($old_thread_age_count_log_delimiter, @{$validlog_array_ref}) . "\n";
    }
    truncate($old_thread_age_count_log_fh, tell($old_thread_age_count_log_fh));

    # クローズ
    close($old_thread_age_count_log_fh);
}

1;
