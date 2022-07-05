package ThreadCreatePostRestrict;
use strict;

use open IO => ':encoding(cp932)';

use Encode qw();
use Carp qw(croak confess);
use Scalar::Util qw(blessed);
use List::MoreUtils qw(uniq);

use Matcher::Utils;

my Encode::Encoding $enc_cp932 = defined($main::enc_cp932) ? $main::enc_cp932 : Encode::find_encoding('cp932');

# 判定結果定数定義
use constant {
    RESULT_NO_RESTRICTED                                          => 0,
    RESULT_THREAD_CREATE_RESTRICT_TYPE_1                          => 1,
    RESULT_THREAD_CREATE_RESTRICT_TYPE_2                          => 1 << 1,
    RESULT_THREAD_CREATE_RESTRICT_TYPE_3                          => 1 << 2,
    RESULT_THREAD_CREATE_RESTRICT_TYPE_4                          => 1 << 3,
    RESULT_THREAD_CREATE_RESTRICT_TYPE_5                          => 1 << 4,
    RESULT_POST_RESTRICT_BY_THREAD_TITLE_THREAD_CREATOR_EXCLUSION => 1 << 5,
    RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_1                   => 1 << 6,
    RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_2                   => 1 << 7,
    RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_3                   => 1 << 8,
    RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_4                   => 1 << 9,
    RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_5                   => 1 << 10
};

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

# 外部ファイルで指定された日時とCookieA発行日時を比較し、
# 除外対象であるかどうかを返すサブルーチン
sub is_except_cookie_a_issue_datetime {
    my ($reference_datetime_str, $cookie_a_length, $cookie_issue_datetime_num) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }

    if ($cookie_a_length != 12 && $cookie_a_length != 14) {
        # CookieAの桁数が正しくない場合は、除外対象ではない
        return;
    }

    if ($reference_datetime_str !~ /^\d{2}(\d{2})\/(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[0-1]) ([01]\d|2[0-3]):([0-5]\d)$/) {
        # 外部ファイル指定日時が、想定するフォーマットでない場合は除外対象ではない
        return;
    }

    # CookieAの値が12桁の場合はすべて除外対象
    if ($cookie_a_length == 12) {
        return 1;
    }

    # 外部ファイル指定日時 数値表現を作成
    my $reference_datetime_num = int("$1$2$3$4$5");

    # CookieA発行日時 が 外部ファイル指定日時 未満であるかどうかを返す
    return $cookie_issue_datetime_num < $reference_datetime_num;
}

# 外部ファイルで指定されたCookieA,登録ID,書込IDに完全一致して
# 除外対象であるかどうかを返すサブルーチン
sub is_except_cookie_a_user_id_history_id {
    my ($target_str, $cookie_a, $user_id, $history_id) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }

    if ($target_str eq '') {
        # 対象設定文字列が空の場合は除外対象判定を行わない
        return;
    }

    # 「*」が指定され、登録IDか書込IDのいずれかが存在する場合はすべて除外対象
    if ($target_str eq '*' && ($user_id ne '' || $history_id ne '')) {
        return 1;
    }

    # 一致判定対象 CookieA, 登録ID, 書込IDをハッシュのキーとして取得
    my %value_existent_elements = map { $_ => undef } grep { $_ ne '' } ($cookie_a, $user_id, $history_id);
    if (scalar(keys(%value_existent_elements)) == 0) {
        # 一致判定対象がない場合は、除外対象判定を行わない
        return;
    }

    # 指定文字列を「,」で分割
    my @targets = grep { $_ ne '' } split(/,/, $target_str, -1);

    # 一致判定対象ハッシュのキーに存在するかどうかで
    # 完全一致判定を行い、一致したかどうかを返す
    foreach my $target (@targets) {
        if (exists($value_existent_elements{$target})) {
            # 一致した
            return 1;
        }
    }
    # いずれにも一致しなかった
    return;
}

sub new {
    my $class = shift;
    my ($matcher_utils_instance,
        $setting_filepath,
        $host, $useragent, $cookie_a, $user_id, $history_id, $is_private_browsing_mode,
        $cookie_a_instance) = @_;
    arg_check(
        9,
        [
            'Matcher::Utils',
            '',
            '', '', '', '', '', '',
            'UniqueCookie'
        ],
        @_
    );

    # Matcher::Utilsインスタンス取得
    my Matcher::Utils $mu = $matcher_utils_instance;

    # CookieA 桁数を取得
    my $cookie_a_length = length($cookie_a);

    # CookieA発行日時 数値表現を作成 (現在のCookieA発行形式に限る)
    my $cookie_a_issue_datetime_num;
    if ($cookie_a =~ /^(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[0-1]))_.._((?:[01]\d|2[0-3])[0-5]\d)$/) {
        $cookie_a_issue_datetime_num = int("$1$2");
    }

    my %self = (
        MATCHER_UTILS_INSTANCE => $matcher_utils_instance,
        HOST                   => $host,
        COOKIE_A               => $cookie_a,
        USER_ID                => $user_id,
        HISTORY_ID             => $history_id
    );

    # 外部ファイルをパース
    my $thread_create_restrict_status = RESULT_NO_RESTRICTED; # スレッド作成制限機能 制限対象判定結果
    my @valid_setting_pairs_of_post_restrict_by_thread_title; # スレッドタイトルによる書き込み制限機能 有効設定配列
    my $disable_setting_char = $enc_cp932->decode('▼');

    # 外部ファイルオープン
    open(my $setting_fh, '<', $setting_filepath) || croak("Open error: $setting_filepath");
    flock($setting_fh, 1) || croak("Lock error: $setting_filepath");
    $self{SETTING_FH} = $setting_fh;

    # ヘッダ行(2行)読み飛ばし
    <$setting_fh>;
    <$setting_fh>;

    # スレタイによる制限の除外(指定) の条件分割文字を定義
    my $thread_title_post_restrict_exemption_condition_split_regex;
    {
        my $decoded_char = $enc_cp932->decode('●');
        $thread_title_post_restrict_exemption_condition_split_regex = qr/$decoded_char/;
    }

    # 有効な設定行を読み込み
    while (my $line = <$setting_fh>) {
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @settings = split(/\^/, $line, -1);
        if (scalar(@settings) != 20 || $settings[1] eq $disable_setting_char) {
            # 20列ではないログ行、もしくは、無効列に▼の列はスキップ
            next;
        }

        # ホストとUserAgent・CookieA or 登録ID or 書込ID・プライベートモード・CookieAの有無・時間範囲指定・期間指定・スレ作成制限・スレタイによる制限について、
        # 「-」を空文字列に置き換える
        foreach my $i (2 .. 7, 10, 12) {
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

        # CookieAの有無列が1の場合に対象判定
        # (未発行の場合が対象のため、発行されている場合はスキップ)
        if ($settings[5] eq '1' && $cookie_a_instance->is_issued()) {
            next;
        }

        # 「ホストとUserAgent」か「CookieA or 登録ID or 書込ID」のいずれかで一致したかどうかのフラグ
        my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;

        # ホストとUserAgentの一致判定
        my @host_useragent_match_array = ([], []);
        if ($settings[2] ne '') {
            my ($host_useragent_match_array_ref) =
                @{ $mu->get_matched_host_useragent_and_whether_its_not_match(
                    $host, $useragent, $settings[2], ['**', '**'], Matcher::Utils::UTF8_FLAG_FORCE_ON
                ) };
            if (defined($host_useragent_match_array_ref)) {
                @host_useragent_match_array = @{$host_useragent_match_array_ref};
                $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
            }
        }

        # CookieA or 登録ID or 書込IDの一致判定
        my @cookiea_userid_historyid_match_array = ([], [], []);
        if ($settings[3] ne '') {
            my ($cookiea_userid_historyid_match_array_ref) =
                @{ $mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match(
                    $cookie_a, $user_id, $history_id, $settings[3], Matcher::Utils::UTF8_FLAG_FORCE_ON
                ) };
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
        if ($settings[6] ne '') {
            if ($mu->is_in_time_range($settings[6], undef())) {
                @match_time_range_array = ($settings[6]);
            } else {
                next;
            }
        }

        # 期間指定・経過時間の一致判定
        if ($settings[7] ne '' && $settings[8] ne '') {
            if (!$mu->is_within_validity_period($settings[7], $settings[8], undef())) {
                next;
            }
        }

        # スレッド作成制限機能の判定
        if ($settings[10] ne '') {
            # 制限タイプを確定
            my $currentset_thread_create_restrict_status = RESULT_NO_RESTRICTED;
            if ($settings[10] eq '1') {
                $currentset_thread_create_restrict_status |= RESULT_THREAD_CREATE_RESTRICT_TYPE_1;
            } elsif ($settings[10] eq '2') {
                $currentset_thread_create_restrict_status |= RESULT_THREAD_CREATE_RESTRICT_TYPE_2;
            } elsif ($settings[10] eq '3') {
                $currentset_thread_create_restrict_status |= RESULT_THREAD_CREATE_RESTRICT_TYPE_3;
            } elsif ($settings[10] eq '4') {
                $currentset_thread_create_restrict_status |= RESULT_THREAD_CREATE_RESTRICT_TYPE_4;
            } elsif ($settings[10] eq '5') {
                $currentset_thread_create_restrict_status |= RESULT_THREAD_CREATE_RESTRICT_TYPE_5;
            }

            # 制限対象だった場合、
            # スレ作成制限の除外(日付) もしくは スレ作成制限の除外(指定) の対象であるかどうか判定
            if ($currentset_thread_create_restrict_status != RESULT_NO_RESTRICTED
                && (is_except_cookie_a_issue_datetime($settings[15], $cookie_a_length, $cookie_a_issue_datetime_num)
                    || is_except_cookie_a_user_id_history_id($settings[16], $cookie_a, $user_id, $history_id)
                )
            ) {
                $currentset_thread_create_restrict_status = RESULT_NO_RESTRICTED;
            }

            # 判定結果を統合
            $thread_create_restrict_status |= $currentset_thread_create_restrict_status;
        }

        # スレッドタイトルによる書き込み制限機能 有効設定を保存
        if ($settings[12] ne '' && $settings[13] ne '') {
            # 制限タイプを確定
            my $restrict_type;
            if ($settings[12] eq '1') {
                $restrict_type = RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_1;
            } elsif ($settings[12] eq '2') {
                $restrict_type = RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_2;
            } elsif ($settings[12] eq '3') {
                $restrict_type = RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_3;
            } elsif ($settings[12] eq '4') {
                $restrict_type = RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_4;
            } elsif ($settings[12] eq '5') {
                $restrict_type = RESULT_POST_RESTRICT_BY_THREAD_TITLE_TYPE_5;
            }

            # 制限対象だった場合、
            # スレタイによる制限の除外(日付) もしくは スレタイによる制限の除外(指定) の対象であるかどうか判定
            my @exempt_thread_titles; # 除外スレッドタイトル設定配列
            if (defined($restrict_type)) {
                if (is_except_cookie_a_issue_datetime($settings[18], $cookie_a_length, $cookie_a_issue_datetime_num)) {
                    # スレタイによる制限の除外(日付) の対象だった場合、除外
                    $restrict_type = undef;
                } else {
                    # スレタイによる制限の除外(指定) 対象判定

                    # 「●」による複数条件ループ
                    foreach my $condition_str (split($thread_title_post_restrict_exemption_condition_split_regex, $settings[19])) {
                        # CookieA/登録ID/書込IDとスレッドタイトルの対象文字列を分割
                        my ($target_cookie_a_user_id_history_ids, $target_thread_title) = split(/<>/, $condition_str, 2);

                        # 条件が正しくない場合や、CookieA/登録ID/書込IDが一致しない場合はスキップ
                        if (!defined($target_cookie_a_user_id_history_ids)
                            || (defined($target_thread_title) && $target_thread_title eq '')
                            || !is_except_cookie_a_user_id_history_id($target_cookie_a_user_id_history_ids, $cookie_a, $user_id, $history_id)
                        ) {
                            next;
                        }

                        # 対象スレッドタイトル確定
                        if (!defined($target_thread_title)) {
                            # 指定がない場合は、スレッドタイトル列の値を除外対象とする
                            $target_thread_title = $settings[13];
                        }

                        # 除外スレッドタイトル設定配列に追加
                        push(@exempt_thread_titles, $target_thread_title);
                    }
                }
            }

            # 制限タイプを確定できた場合のみ、有効設定として配列に追加
            if (defined($restrict_type)) {
                push(
                    @valid_setting_pairs_of_post_restrict_by_thread_title,
                    [$restrict_type, $settings[13], join(',', uniq(@exempt_thread_titles))]
                );
            }
        }
    }
    $self{THREAD_CREATE_RESTRICT_STATUS} = $thread_create_restrict_status;
    $self{VALID_SETTING_PAIRS_OF_POST_RESTRICT_BY_THREAD_TITLE} = \@valid_setting_pairs_of_post_restrict_by_thread_title;

    # クロージャ定義
    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }
        arg_check(1, [''], @_);

        # 引数として与えられたキーに対応する値を返す
        my $key = shift;
        if (!exists($self{$key})) {
            confess("key not found: $key");
        }
        return $self{$key};
    };

    return bless $closure, $class;
}

sub DESTROY {
    my $self = shift;

    # 外部ファイルハンドラ クローズ
    my $setting_fh = $self->('SETTING_FH');
    close($setting_fh);
}

sub determine_thread_create_restrict_status {
    my $self = shift;
    if (!defined(blessed($self)) || !$self->isa('ThreadCreatePostRestrict')) {
        confess('call me only in instance variable.');
    }
    arg_check(0, [], @_);

    return $self->('THREAD_CREATE_RESTRICT_STATUS');
}

sub determine_post_restrict_status_by_thread_title {
    my $self = shift;
    my ($thread_title, $firstres_host, $firstres_url, $firstres_user_id, $firstres_cookie_a, $firstres_history_id) = @_;
    if (!defined(blessed($self)) || !$self->isa('ThreadCreatePostRestrict')) {
        confess('call me only in instance variable.');
    }
    arg_check(6, ['', '', '', '', '', ''], @_);

    # Matcher::Utilsインスタンス取得
    my Matcher::Utils $mu = $self->('MATCHER_UTILS_INSTANCE');

    my $status = RESULT_NO_RESTRICTED;

    # スレッドタイトルによる書き込み制限機能のスレッド作成者の除外機能 判定
    if ($firstres_url eq 'jogai'
        && (
            ($firstres_host ne '' && $self->('HOST') eq $firstres_host)
            || ($firstres_user_id ne '' && $self->('USER_ID') eq $firstres_user_id)
            || ($firstres_cookie_a ne '' && $self->('COOKIE_A') eq $firstres_cookie_a)
            || ($firstres_history_id ne '' && $self->('HISTORY_ID') eq $firstres_history_id)
        )
    ) {
        $status |= RESULT_POST_RESTRICT_BY_THREAD_TITLE_THREAD_CREATOR_EXCLUSION;
    }

    # スレッド名判定
    #
    # スレタイによる制限の除外(指定)の対象ではないスレッド名を対象に、
    # スレタイによる制限の一致判定を行って、制限タイプを確定させる
    foreach my $setting_pair (@{$self->('VALID_SETTING_PAIRS_OF_POST_RESTRICT_BY_THREAD_TITLE')}) {
        my ($restrict_type, $target_thread_title, $exempt_thread_title) = @{$setting_pair};

        # スレタイによる制限の除外(指定)の対象判定
        my ($exempt_result_array_ref) =
            @{ $mu->get_matched_thread_title_to_setting_and_whether_its_not_match(
                $thread_title, $exempt_thread_title, undef(), undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON
            ) };
        if (defined($exempt_result_array_ref)) {
            next;
        }

        # スレタイによる制限の一致判定
        my ($result_array_ref) =
            @{ $mu->get_matched_thread_title_to_setting_and_whether_its_not_match(
                $thread_title, $target_thread_title, undef(), undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON
            ) };
        if (defined($result_array_ref)) {
            $status |= $restrict_type;
        }
    }

    return $status;
}

1;
