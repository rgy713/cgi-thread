#!/usr/local/bin/perl

BEGIN {
    # 外部ファイル取り込み
    require './init.cgi';
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use JSON::XS;
use HistoryCookie;
use HistoryLog;

# 時刻取得
my ($time) = get_time();

# HTTPステータスコード定義
my $HTTP_STATUS_204_NO_CONTENT             = "Status: 204 No Content\n";
my $HTTP_STATUS_400_BAD_REQUEST            = "Status: 400 Bad Request\n";
my $HTTP_STATUS_403_FORBIDDEN              = "Status: 403 Forbidden\n";
my $HTTP_STATUS_404_NOT_FOUND              = "Status: 404 Not Found\n";
my $HTTP_STATUS_405_METHOD_NOT_ALLOWED     = "Status: 405 Method Not Allowed\n";
my $HTTP_STATUS_410_GONE                   = "Status: 410 Gone\n";
my $HTTP_STATUS_415_UNSUPPORTED_MEDIA_TYPE = "Status: 415 Unsupported Media Type\n";
my $HTTP_STATUS_500_INTERNAL_SERVER_ERROR  = "Status: 500 Internal Server Error\n";
my $HTTP_STATUS_503_SERVICE_UNAVAILABLE    = "Status: 503 Service Unavailable\n";

if ($ENV{REQUEST_METHOD} ne 'POST') {
    # POST以外のアクセスを拒否(405 Method Not Allowedを返す)
    output_http_header($HTTP_STATUS_405_METHOD_NOT_ALLOWED);
    exit();
} elsif (!exists($ENV{CONTENT_TYPE}) || $ENV{CONTENT_TYPE} !~ /^application\/json(?:;.*|\s*)?$/) {
    # Content-Typeがapplication/json以外のアクセスを拒否(415 Unsupported Media Typeを返す)
    output_http_header($HTTP_STATUS_415_UNSUPPORTED_MEDIA_TYPE);
    exit();
}

# POSTされたpayloadをURLデコードして取得
my $payload;
{
    my $post_data;
    read(STDIN, $post_data, $ENV{CONTENT_LENGTH});
    foreach my $pair (split(/&/, $post_data)) {
        my ($key, $value) = split(/=/, $pair);
        if ($key eq 'payload') {
            $value =~ s/\+/ /go;
            $value =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("C", hex($1))/ego;
            $payload = $value;
            last;
        }
    }
}

# JSONパース
my $json = {};
eval {
    if (defined($payload)) {
        $json = JSON::XS->new()->utf8(1)->decode($payload);
    }
};
if ($@) {
    # Payloadが正しくないなどでJSONデコードできない場合は、400 Bad Requestを返す
    output_http_header($HTTP_STATUS_400_BAD_REQUEST);
    exit();
}

# エラー出力終了フラグ
my $error_output_flg = 1;

# ここまで読んだ機能 スレッド追加
if ($json->{mode} eq 'readup_to_here' && int($json->{thread_no}) > 0) {
    # 書込IDを取得
    my $chistory_id = do {
        my $instance = HistoryCookie->new();
        $instance->get_history_id();
    };
    if (!defined($chistory_id)) {
        # 書込IDログインしてない場合は、403 Forbiddenを返す
        output_http_header($HTTP_STATUS_403_FORBIDDEN);
        exit();
    }

    # HistoryLogインスタンスを初期化
    my $history_log = HistoryLog->new($chistory_id);

    # 最新レス情報をスレッドログから取得
    my @log;
    {
        # スレッドログ一括読み込み
        # スレッドログファイルが見つからない場合は 401 Goneを、
        # スレッドログファイルをロックできない場合は、503 Service Unavailableを返す
        my $logfile_path = get_logfolder_path($json->{thread_no}) . '/' . $json->{thread_no} . '.cgi';
        open(my $log_fh, '<', $logfile_path) || output_http_header($HTTP_STATUS_410_GONE) && exit();
        flock($log_fh, 1) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
        while(<$log_fh>) {
            chomp($_);
            push(@log, [split(/<>/)]);
        }
        close($log_fh);
    }
    if (scalar(@log) < 2) {
        # ログ行が2行未満の場合、スレッドログが存在しなかったものとみなし、410 Goneを返す
        output_http_header($HTTP_STATUS_410_GONE);
        exit();
    }
    my $decoded_sub = $enc_cp932->decode(${$log[0]}[1]);
    my ($latest_res_no, $latest_res_time) = @{$log[$#log]}[0, 11];

    # 書き込み履歴機能の除外設定合致判定
    if (scalar(grep { $_ ne '' && index($decoded_sub, $_) != -1 } @history_save_exempt_titles) > 0) {
        # 除外対象だった場合、404 Not Foundを返す
        output_http_header($HTTP_STATUS_404_NOT_FOUND);
        exit();
    }

    # 履歴ログに追加し、成功ステータスコードを返す
    $history_log->add_post_history($json->{thread_no}, $latest_res_no, $latest_res_time);
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # HistoryLogインスタンス 解放
    $history_log->DESTROY();

    # 正常終了
    $error_output_flg = 0;
}

# スレッドNoを自動書き込み禁止機能のレス部分相当で動作する機能
if ($json->{mode} eq 'thread_num_auto_prohibiting'
    && $json->{thread_number} > 0
    && (   $json->{action} eq 'add_1' || $json->{action} eq 'add_2' || $json->{action} eq 'add_3'
        || $json->{action} eq 'add_4' || $json->{action} eq 'add_5' || $json->{action} eq 'add_6'
        || $json->{action} eq 'add_permanently'
        || $json->{action} eq 'remove'
        )
    ) {

    # ログファイルをパースする必要があるかどうか
    my $need_parse_log = -s $auto_post_prohibit_thread_number_res_target_log_path > 2;

    # ログファイルオープン
    open(my $json_log_fh, '+>>', $auto_post_prohibit_thread_number_res_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS インスタンス初期化
    my $json_serializer = JSON::XS->new();

    # ログファイル読み込み・パース処理
    my @load_thread_number_res_target_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSONパースを行う
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_thread_number_res_target_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSONパースに失敗した (内容に異常がある)場合、
            # 500 Internal Server Errorを返す
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # パースした配列の制限設定ハッシュのうち、ログファイルに保存する制限設定ハッシュ配列を作成
    my @save_thread_number_res_target_array;
    foreach my $target_hash_ref (@load_thread_number_res_target_array) {
        # ハッシュリファレンスではない場合はスキップ
        if (ref($target_hash_ref) ne 'HASH') {
            next;
        }
        my %target_hash = %{$target_hash_ref};

        # 必須キーが無い、設定時間を経過した設定、追加/削除するスレッド番号と同じ設定はスキップ
        if (!exists($target_hash{thread_number}) || $target_hash{thread_number} == $json->{thread_number}
            || !exists($target_hash{time})
            || !exists($target_hash{type}) || $target_hash{type} < 0 || $target_hash{type} > 6
            || ($target_hash{type} == 1 && ($target_hash{time} + $auto_post_prohibit_thread_number_res_target_hold_hour_1 * 3600) < $time)
            || ($target_hash{type} == 2 && ($target_hash{time} + $auto_post_prohibit_thread_number_res_target_hold_hour_2 * 3600) < $time)
            || ($target_hash{type} == 3 && ($target_hash{time} + $auto_post_prohibit_thread_number_res_target_hold_hour_3 * 3600) < $time)
            || ($target_hash{type} == 4 && ($target_hash{time} + $auto_post_prohibit_thread_number_res_target_hold_hour_4 * 3600) < $time)
            || ($target_hash{type} == 5 && ($target_hash{time} + $auto_post_prohibit_thread_number_res_target_hold_hour_5 * 3600) < $time)
            || ($target_hash{type} == 6 && ($target_hash{time} + $auto_post_prohibit_thread_number_res_target_hold_hour_6 * 3600) < $time)
        ) {
            next;
        }

        # ログファイルに残す
        push(@save_thread_number_res_target_array, $target_hash_ref);
    }

    # 追加モードのみ、制限設定を追加
    if ($json->{action} ne 'remove') {
        # type値決定
        my $type;
        if ($json->{action} eq 'add_permanently') {
            $type = 0;
        } elsif ($json->{action} eq 'add_1') {
            $type = 1;
        } elsif ($json->{action} eq 'add_2') {
            $type = 2;
        } elsif ($json->{action} eq 'add_3') {
            $type = 3;
        } elsif ($json->{action} eq 'add_4') {
            $type = 4;
        } elsif ($json->{action} eq 'add_5') {
            $type = 5;
        } elsif ($json->{action} eq 'add_6') {
            $type = 6;
        }

        # 追加データを作成
        my %data = (
            thread_number => int($json->{thread_number}),
            time          => $time,
            type          => $type
        );

        # 制限設定を追加
        push(@save_thread_number_res_target_array, \%data);
    }

    # ログファイルを更新
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_thread_number_res_target_array);

    # ログファイルクローズ
    close($json_log_fh);

    # 成功ステータスコードを返す
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # 正常終了
    $error_output_flg = 0;
}

# スレッドタイトルを自動書き込み禁止機能のレス部分相当で動作する機能
if ($json->{mode} eq 'thread_title_auto_prohibiting'
    && defined($json->{thread_title}) && $json->{thread_title} ne ''
    && (((   $json->{action} eq 'add_1' || $json->{action} eq 'add_2' || $json->{action} eq 'add_3'
          || $json->{action} eq 'add_4' || $json->{action} eq 'add_5' || $json->{action} eq 'add_6'
          || $json->{action} eq 'add_permanently'
         )
         && $json->{word_type} >= 1 && $json->{word_type} <= 20
        )
        || $json->{action} eq 'remove'
       )
    ) {
    # ログファイルをパースする必要があるかどうか
    my $need_parse_log = -s $auto_post_prohibit_thread_title_res_target_log_path > 2;

    # ログファイルオープン
    open(my $json_log_fh, '+>>', $auto_post_prohibit_thread_title_res_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS インスタンス初期化
    my $json_serializer = JSON::XS->new();

    # ログファイル読み込み・パース処理
    my @load_thread_title_res_target_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSONパースを行う
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_thread_title_res_target_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSONパースに失敗した (内容に異常がある)場合、
            # 500 Internal Server Errorを返す
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # パースした配列の制限設定ハッシュのうち、ログファイルに保存する制限設定ハッシュ配列を作成
    my @save_thread_title_res_target_array;
    foreach my $target_hash_ref (@load_thread_title_res_target_array) {
        # ハッシュリファレンスではない場合はスキップ
        if (ref($target_hash_ref) ne 'HASH') {
            next;
        }
        my %target_hash = %{$target_hash_ref};

        # 異常設定値、設定時間を経過した設定、追加/削除するスレッドタイトル・制限単語と同じ設定はスキップ
        if (!exists($target_hash{thread_title})
            || !exists($target_hash{type}) || $target_hash{type} < 0 || $target_hash{type} > 6
            || !exists($target_hash{time}) || !defined($target_hash{time})
            || !exists($target_hash{word_type}) || $target_hash{word_type} < 1 || $target_hash{word_type} > 20
            || ($target_hash{type} == 1 && ($target_hash{time} + $auto_post_prohibit_thread_title_res_target_hold_hour_1 * 3600) < $time)
            || ($target_hash{type} == 2 && ($target_hash{time} + $auto_post_prohibit_thread_title_res_target_hold_hour_2 * 3600) < $time)
            || ($target_hash{type} == 3 && ($target_hash{time} + $auto_post_prohibit_thread_title_res_target_hold_hour_3 * 3600) < $time)
            || ($target_hash{type} == 4 && ($target_hash{time} + $auto_post_prohibit_thread_title_res_target_hold_hour_4 * 3600) < $time)
            || ($target_hash{type} == 5 && ($target_hash{time} + $auto_post_prohibit_thread_title_res_target_hold_hour_5 * 3600) < $time)
            || ($target_hash{type} == 6 && ($target_hash{time} + $auto_post_prohibit_thread_title_res_target_hold_hour_6 * 3600) < $time)
            || ($target_hash{thread_title} eq $json->{thread_title} && $target_hash{word_type} == $json->{word_type})
        ) {
            next;
        }

        # ログファイルに残す
        push(@save_thread_title_res_target_array, $target_hash_ref);
    }

    # 追加モードのみ、制限設定を追加
    if ($json->{action} ne 'remove') {
        # type値決定
        my $type;
        if ($json->{action} eq 'add_permanently') {
            $type = 0;
        } elsif ($json->{action} eq 'add_1') {
            $type = 1;
        } elsif ($json->{action} eq 'add_2') {
            $type = 2;
        } elsif ($json->{action} eq 'add_3') {
            $type = 3;
        } elsif ($json->{action} eq 'add_4') {
            $type = 4;
        } elsif ($json->{action} eq 'add_5') {
            $type = 5;
        } elsif ($json->{action} eq 'add_6') {
            $type = 6;
        }

        # 追加
        push(@save_thread_title_res_target_array, {
                thread_title => $json->{thread_title},
                type         => $type,
                time         => $time,
                word_type    => $json->{word_type}
            });
    }

    # ログファイルを更新
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_thread_title_res_target_array);

    # ログファイルクローズ
    close($json_log_fh);

    # 成功ステータスコードを返す
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # 正常終了
    $error_output_flg = 0;
}

# スレッド画面からユーザを制限する機能
# ユーザ制限機能 (CookieAなどをフォームから登録)
if (($json->{mode} eq 'restrict_user_from_thread_page' || $json->{mode} eq 'restrict_user_from_form')
    && ($json->{action} eq 'add_1' || $json->{action} eq 'add_2'
        || $json->{action} eq 'add_3' || $json->{action} eq 'add_4'
        || $json->{action} eq 'add_5' || $json->{action} eq 'add_6'
        || $json->{action} eq 'add_7'
        || $json->{action} eq 'add_permanently' || $json->{action} eq 'remove')) {
    # 書込IDが送られてきた場合は、あらかじめ末尾の@を削除する
    if (exists($json->{history_id})) {
        $json->{history_id} =~ s/\@$//;
    }

    # ログファイルをパースする必要があるかどうか
    my $need_parse_log = -s $restrict_user_from_thread_page_target_log_path > 2;

    # ログファイルオープン
    open(my $json_log_fh, '+>>', $restrict_user_from_thread_page_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS インスタンス初期化
    my $json_serializer = JSON::XS->new();

    # ログファイル読み込み・パース処理
    my @load_restrict_user_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSONパースを行う
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_restrict_user_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSONパースに失敗した (内容に異常がある)場合、
            # 500 Internal Server Errorを返す
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # パースした配列の制限設定ハッシュのうち、ログファイルに保存する制限設定ハッシュ配列を作成
    my @save_restrict_user_array;
    foreach my $setting_ref (@load_restrict_user_array) {
        # ハッシュリファレンスではない場合はスキップ
        if (ref($setting_ref) ne 'HASH') {
            next;
        }

        # 異常設定値、設定時間を経過した設定はスキップ
        if (!exists($setting_ref->{type}) || $setting_ref->{type} < 0 || $setting_ref->{type} > 7
            || !exists($setting_ref->{time}) || $setting_ref->{time} < 0
            || ($setting_ref->{type} == 1 && (($setting_ref->{time} + $restrict_user_from_thread_page_target_hold_hour_1 * 3600) < $time))
            || ($setting_ref->{type} == 2 && (($setting_ref->{time} + $restrict_user_from_thread_page_target_hold_hour_2 * 3600) < $time))
            || ($setting_ref->{type} == 3 && (($setting_ref->{time} + $restrict_user_from_thread_page_target_hold_hour_3 * 3600) < $time))
            || ($setting_ref->{type} == 4 && (($setting_ref->{time} + $restrict_user_from_thread_page_target_hold_hour_4 * 3600) < $time))
            || ($setting_ref->{type} == 5 && (($setting_ref->{time} + $restrict_user_from_thread_page_target_hold_hour_5 * 3600) < $time))
            || ($setting_ref->{type} == 6 && (($setting_ref->{time} + $restrict_user_from_thread_page_target_hold_hour_6 * 3600) < $time))
            || ($setting_ref->{type} == 7 && (($setting_ref->{time} + $restrict_user_from_thread_page_target_hold_hour_7 * 3600) < $time))
            || ($setting_ref->{cookie_a} eq '' && $setting_ref->{history_id} eq '' && $setting_ref->{host} eq '' && $setting_ref->{user_id} eq '')) {
            next;
        }

        # 既存の設定から、追加/削除する際に部分一致する設定を削除
        foreach my $key ('cookie_a', 'history_id', 'host', 'user_id') {
            if ($setting_ref->{$key} ne '' && $setting_ref->{$key} eq $json->{$key}) {
                delete($setting_ref->{$key});
            }
        }
        if (scalar(keys(%{$setting_ref})) < 3) {
            # 制限項目が残らなかった設定はスキップ
            next;
        }

        # ログファイルに残す
        push(@save_restrict_user_array, $setting_ref);
    }

    # 追加モードのみ、制限設定を追加
    if ($json->{action} ne 'remove') {
        # type値決定
        my $type;
        if ($json->{action} eq 'add_permanently') {
            $type = 0;
        } elsif ($json->{action} eq 'add_1') {
            $type = 1;
        } elsif ($json->{action} eq 'add_2') {
            $type = 2;
        } elsif ($json->{action} eq 'add_3') {
            $type = 3;
        } elsif ($json->{action} eq 'add_4') {
            $type = 4;
        } elsif ($json->{action} eq 'add_5') {
            $type = 5;
        } elsif ($json->{action} eq 'add_6') {
            $type = 6;
        } elsif ($json->{action} eq 'add_7') {
            $type = 7;
        }

        # 追加対象キーを決定
        my @target = grep { $json->{$_} ne '' } ('cookie_a', 'history_id', 'user_id');
        if ($json->{host} ne ''
            && scalar(grep { $_ ne '' && index($json->{host}, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0) {
            # ホストは、@ngthread_thread_list_creator_name_override_exclude_hostsに部分一致しない場合のみ追加対象とする
            push(@target, 'host');
        }

        # 追加
        if (scalar(@target) > 0) {
            my $add_setting_ref = {
                type  => $type,
                time  => $time
            };
            foreach my $key (@target) {
                $add_setting_ref->{$key} = $json->{$key};
            }
            push(@save_restrict_user_array, $add_setting_ref)
        }
    }

    # ログファイルを更新
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_restrict_user_array);

    # ログファイルクローズ
    close($json_log_fh);

    # 成功ステータスコードを返す
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # 正常終了
    $error_output_flg = 0;
}

# スレッド画面からユーザを時間制限する機能
if ($json->{mode} eq 'restrict_user_from_thread_page_by_time_range'
    && ($json->{action} eq 'add_1' || $json->{action} eq 'add_2'
        || $json->{action} eq 'add_3' || $json->{action} eq 'add_4'
        || $json->{action} eq 'add_permanently' || $json->{action} eq 'remove')) {
    # 書込IDが送られてきた場合は、あらかじめ末尾の@を削除する
    if (exists($json->{history_id})) {
        $json->{history_id} =~ s/\@$//;
    }

    # ログファイルをパースする必要があるかどうか
    my $need_parse_log = -s $restrict_user_from_thread_page_by_time_range_target_log_path > 2;

    # ログファイルオープン
    open(my $json_log_fh, '+>>', $restrict_user_from_thread_page_by_time_range_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS インスタンス初期化
    my $json_serializer = JSON::XS->new();

    # ログファイル読み込み・パース処理
    my @load_restrict_user_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSONパースを行う
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_restrict_user_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSONパースに失敗した (内容に異常がある)場合、
            # 500 Internal Server Errorを返す
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # パースした配列の制限設定ハッシュのうち、ログファイルに保存する制限設定ハッシュ配列を作成
    my @save_restrict_user_array;
    foreach my $setting_ref (@load_restrict_user_array) {
        # ハッシュリファレンスではない場合はスキップ
        if (ref($setting_ref) ne 'HASH') {
            next;
        }

        # 異常設定値、設定時間を経過した設定はスキップ
        if (!exists($setting_ref->{type}) || $setting_ref->{type} < 0 || $setting_ref->{type} > 4
            || !exists($setting_ref->{time}) || $setting_ref->{time} < 0
            || ($setting_ref->{type} == 1 && (($setting_ref->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_1 * 3600) < $time))
            || ($setting_ref->{type} == 2 && (($setting_ref->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_2 * 3600) < $time))
            || ($setting_ref->{type} == 3 && (($setting_ref->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_3 * 3600) < $time))
            || ($setting_ref->{type} == 4 && (($setting_ref->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_4 * 3600) < $time))
            || ($setting_ref->{cookie_a} eq '' && $setting_ref->{history_id} eq '' && $setting_ref->{host} eq '' && $setting_ref->{user_id} eq '')) {
            next;
        }

        # 既存の設定から、追加/削除する際に部分一致する設定を削除
        foreach my $key ('cookie_a', 'history_id', 'host', 'user_id') {
            if ($setting_ref->{$key} ne '' && $setting_ref->{$key} eq $json->{$key}) {
                delete($setting_ref->{$key});
            }
        }
        if (scalar(keys(%{$setting_ref})) < 3) {
            # 制限項目が残らなかった設定はスキップ
            next;
        }

        # ログファイルに残す
        push(@save_restrict_user_array, $setting_ref);
    }

    # 追加モードのみ、制限設定を追加
    if ($json->{action} ne 'remove') {
        # type値決定
        my $type;
        if ($json->{action} eq 'add_permanently') {
            $type = 0;
        } elsif ($json->{action} eq 'add_1') {
            $type = 1;
        } elsif ($json->{action} eq 'add_2') {
            $type = 2;
        } elsif ($json->{action} eq 'add_3') {
            $type = 3;
        } elsif ($json->{action} eq 'add_4') {
            $type = 4;
        }

        # 追加対象キーを決定
        my @target = grep { $json->{$_} ne '' } ('cookie_a', 'history_id', 'user_id');
        if ($json->{host} ne ''
            && scalar(grep { $_ ne '' && index($json->{host}, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0) {
            # ホストは、@ngthread_thread_list_creator_name_override_exclude_hostsに部分一致しない場合のみ追加対象とする
            push(@target, 'host');
        }

        # 追加
        if (scalar(@target) > 0) {
            my $add_setting_ref = {
                type  => $type,
                time  => $time
            };
            foreach my $key (@target) {
                $add_setting_ref->{$key} = $json->{$key};
            }
            push(@save_restrict_user_array, $add_setting_ref)
        }
    }

    # ログファイルを更新
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_restrict_user_array);

    # ログファイルクローズ
    close($json_log_fh);

    # 成功ステータスコードを返す
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # 正常終了
    $error_output_flg = 0;
}

# スレッド画面からユーザを制限する機能 (そのスレのみ)
if ($json->{mode} eq 'in_thread_only_restrict_user_from_thread_page'
    && $json->{thread_number} > 0
    && ($json->{action} eq 'add' || $json->{action} eq 'remove')) {
    # 書込IDが送られてきた場合は、あらかじめ末尾の@を削除する
    if (exists($json->{history_id})) {
        $json->{history_id} =~ s/\@$//;
    }

    # ログファイルをパースする必要があるかどうか
    my $need_parse_log = -s $in_thread_only_restrict_user_from_thread_page_target_log_path > 2;

    # ログファイルオープン
    open(my $json_log_fh, '+>>', $in_thread_only_restrict_user_from_thread_page_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS インスタンス初期化
    my $json_serializer = JSON::XS->new();

    # ログファイル読み込み・パース処理
    my %load_restrict_user_hash;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSONパースを行う
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'HASH') {
                %load_restrict_user_hash = %{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSONパースに失敗した (内容に異常がある)場合、
            # 500 Internal Server Errorを返す
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # パースした制限設定ハッシュのうち、ログファイルに保存する制限設定ハッシュ配列を作成
    my %save_restrict_user_hash;
    while (my ($thread_number, $settings_array_ref) = each(%load_restrict_user_hash)) {
        # 異常スレッドNoはスキップ
        if ($thread_number <= 0) {
            next;
        }
        # 値が配列リファレンスではない場合はスキップ
        if (ref($settings_array_ref) ne 'ARRAY') {
            next;
        }

        # 同じスレッドNoかどうか
        my $is_same_thread_number = $thread_number == $json->{thread_number};

        # 保存対象 スレッドNo内制限設定ハッシュの配列
        my @save_restrict_user_hash_array_in_thread;

        # スレッドNo内 制限設定配列ループ
        foreach my $setting_ref (@{$settings_array_ref}) {
            # ハッシュリファレンスではない場合はスキップ
            if (ref($setting_ref) ne 'HASH') {
                next;
            }

            # 異常設定値、設定時間を経過した設定はスキップ
            if (!exists($setting_ref->{time}) || $setting_ref->{time} < 0
                || (($setting_ref->{time} + $in_thread_only_restrict_user_from_thread_page_target_hold_hour * 3600) < $time)
                || ($setting_ref->{cookie_a} eq '' && $setting_ref->{history_id} eq '' && $setting_ref->{host} eq '' && $setting_ref->{user_id} eq '')) {
                next;
            }

            # 同じスレッドNoの場合に、既存の設定から、追加/削除する際に部分一致する設定を削除
            if ($is_same_thread_number) {
                foreach my $key ('cookie_a', 'history_id', 'host', 'user_id') {
                    if ($setting_ref->{$key} ne '' && $setting_ref->{$key} eq $json->{$key}) {
                        delete($setting_ref->{$key});
                    }
                }
            }

            # 制限項目が残らなかった設定はスキップ
            if (scalar(keys(%{$setting_ref})) < 2) {
                next;
            }

            # 保存対象 スレッドNo内制限設定配列に追加
            push(@save_restrict_user_hash_array_in_thread, $setting_ref);
        }

        # 保存対象 スレッドNo内制限設定ハッシュ配列に1つ以上設定があるときは、
        # ログ保存制限設定ハッシュに追加
        if (scalar(@save_restrict_user_hash_array_in_thread) > 0) {
            $save_restrict_user_hash{$thread_number} = \@save_restrict_user_hash_array_in_thread;
        }
    }

    # 追加モードのみ、制限設定を追加
    if ($json->{action} ne 'remove') {
        # 追加対象キーを決定
        my @target = grep { $json->{$_} ne '' } ('cookie_a', 'history_id', 'user_id');
        if ($json->{host} ne ''
            && scalar(grep { $_ ne '' && index($json->{host}, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0) {
            # ホストは、@ngthread_thread_list_creator_name_override_exclude_hostsに部分一致しない場合のみ追加対象とする
            push(@target, 'host');
        }

        # 追加
        if (scalar(@target) > 0) {
            my $add_setting_ref = {
                time  => $time
            };
            foreach my $key (@target) {
                $add_setting_ref->{$key} = $json->{$key};
            }
            if (exists($save_restrict_user_hash{$json->{thread_number}})) {
                push(@{$save_restrict_user_hash{$json->{thread_number}}}, $add_setting_ref);
            } else {
                $save_restrict_user_hash{$json->{thread_number}} = [$add_setting_ref];
            }
        }
    }

    # ログファイルを更新
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\%save_restrict_user_hash);

    # ログファイルクローズ
    close($json_log_fh);

    # 成功ステータスコードを返す
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # 正常終了
    $error_output_flg = 0;
}

# ユーザ強調表示機能
if (($json->{mode} eq 'highlight_userinfo' || $json->{mode} eq 'highlight_userinfo_from_form')
    && ($json->{action} eq 'add' || $json->{action} eq 'remove')) {
    # 書込IDが送られてきた場合は、あらかじめ末尾の@を削除する
    if (exists($json->{history_id})) {
        $json->{history_id} =~ s/\@$//;
    }

    # ログファイルをパースする必要があるかどうか
    my $need_parse_log = -s $highlight_userinfo_log_path > 2;

    # ログファイルオープン
    open(my $json_log_fh, '+>>', $highlight_userinfo_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS インスタンス初期化
    my $json_serializer = JSON::XS->new();

    # ログファイル読み込み・パース処理
    my @load_highlight_hashref_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSONパースを行う
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_highlight_hashref_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSONパースに失敗した (内容に異常がある)場合、
            # 500 Internal Server Errorを返す
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # パースした強調表示情報ハッシュリファレンス配列を、ログファイルに保存するもののみとなるようフィルタ
    my @save_highlight_hashref_array;
    foreach my $highlight_hashref (@load_highlight_hashref_array) {
        # 値がハッシュリファレンスではない場合はスキップ
        if (ref($highlight_hashref) ne 'HASH') {
            next;
        }

        # 強調表示タイプがセットされていない場合、ユーザ強調表示とみなす
        if (!exists($highlight_hashref->{type})) {
            $highlight_hashref->{type} = 1;
        }

        # 強調表示タイプがユーザ強調表示だった場合、フィルター処理
        # それ以外の強調表示タイプはそのままとする
        if ($highlight_hashref->{type} == 1) {
            # 異常設定値、設定時間を経過した設定はスキップ
            if (!exists($highlight_hashref->{time}) || $highlight_hashref->{time} < 0
                || ($highlight_hashref->{time} + $highlight_userinfo_hold_hour * 3600) <= $time
                || !exists($highlight_hashref->{color}) || $highlight_hashref->{color} < 1
                || ($highlight_hashref->{cookie_a} eq '' && $highlight_hashref->{history_id} eq '' && $highlight_hashref->{host} eq '' && $highlight_hashref->{user_id} eq '')) {
                next;
            }

            # 既存の設定から、追加/削除する際に部分一致する設定を削除
            foreach my $key ('cookie_a', 'history_id', 'host', 'user_id') {
                if ($highlight_hashref->{$key} ne '' && $highlight_hashref->{$key} eq $json->{$key}) {
                    delete($highlight_hashref->{$key});
                }
            }

            # 制限項目が残らなかった設定はスキップ
            if (scalar(keys(%{$highlight_hashref})) < 4) {
                next;
            }
        }

        # 保存対象 強調表示情報ハッシュリファレンス配列に追加
        push(@save_highlight_hashref_array, $highlight_hashref);
    }

    # 追加モードのみ、強調表示設定を追加
    if ($json->{action} eq 'add') {
        # 追加対象キーを決定
        my @target = grep { $json->{$_} ne '' } ('cookie_a', 'history_id', 'user_id');
        if ($json->{host} ne ''
            && scalar(grep { $_ ne '' && index($json->{host}, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0) {
            # ホストは、@ngthread_thread_list_creator_name_override_exclude_hostsに部分一致しない場合のみ追加対象とする
            push(@target, 'host');
        }

        # 追加
        if (scalar(@target) > 0) {
            my $add_userinfo_hashref = {
                color => int($json->{color}),
                time  => $time,
                type  => 1
            };
            foreach my $key (@target) {
                $add_userinfo_hashref->{$key} = $json->{$key};
            }
            push(@save_highlight_hashref_array, $add_userinfo_hashref);
        }
    }

    # ログファイルを更新
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_highlight_hashref_array);

    # ログファイルクローズ
    close($json_log_fh);

    # 成功ステータスコードを返す
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # 正常終了
    $error_output_flg = 0;
}

# UserAgentの強調表示機能
if ($json->{mode} eq 'highlight_ua_from_form'
    && ($json->{action} eq 'add' || $json->{action} eq 'update_timestamp' || $json->{action} eq 'remove')
    && $json->{host} ne ''
    && $json->{useragent} ne '') {

    # ログファイルをパースする必要があるかどうか
    my $need_parse_log = -s $highlight_userinfo_log_path > 2;

    # ログファイルオープン
    open(my $json_log_fh, '+>>', $highlight_userinfo_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS インスタンス初期化
    my $json_serializer = JSON::XS->new();

    # ログファイル読み込み・パース処理
    my @load_highlight_hashref_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSONパースを行う
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_highlight_hashref_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSONパースに失敗した (内容に異常がある)場合、
            # 500 Internal Server Errorを返す
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # パースした強調表示情報ハッシュリファレンス配列を、ログファイルに保存するもののみとなるようフィルタ
    my @save_highlight_hashref_array;
    my $modified_flag;
    foreach my $highlight_hashref (@load_highlight_hashref_array) {
        # 値がハッシュリファレンスではない場合はスキップ
        if (ref($highlight_hashref) ne 'HASH') {
            next;
        }

        # 強調表示タイプがセットされていない場合、ユーザ強調表示とみなす
        if (!exists($highlight_hashref->{type})) {
            $highlight_hashref->{type} = 1;
        }

        # 強調表示タイプがUserAgent強調表示だった場合、フィルター処理
        # それ以外の強調表示タイプはそのままとする
        if ($highlight_hashref->{type} == 2) {
            # 異常設定値はスキップ
            if (!exists($highlight_hashref->{time}) || $highlight_hashref->{time} < 0
                || !exists($highlight_hashref->{color}) || $highlight_hashref->{color} < 1
                || ($highlight_hashref->{host} eq '' && $highlight_hashref->{useragent} eq '')) {
                next;
            }

            # 同じホスト・同じUserAgentの設定が送られてきた場合に、
            # 登録・削除では、その設定をスキップ、
            # タイムスタンプ更新では、タイムスタンプを更新する
            if ($highlight_hashref->{host} eq $json->{host}
                && $highlight_hashref->{useragent} eq $json->{useragent}) {
                $modified_flag = 1;
                if ($json->{action} eq 'add' || $json->{action} eq 'remove') {
                    next;
                } else { # $json->{action} eq 'update_timestamp'
                    $highlight_hashref->{time} = $time;
                }
            }
        }

        # 保存対象 強調表示情報ハッシュリファレンス配列に追加
        push(@save_highlight_hashref_array, $highlight_hashref);
    }

    if ($json->{action} eq 'add') {
        # 追加モードのみ、強調表示設定を追加
        my $add_hashref = {
            color     => int($json->{color}),
            host      => $json->{host},
            time      => $time,
            type      => 2,
            useragent => $json->{useragent}
        };
        unshift(@save_highlight_hashref_array, $add_hashref); # 一致判定の際、新しい設定の一致を優先させるため、先頭に追加

        # 設定時間を経過した設定を除く
        @save_highlight_hashref_array = grep { ($_->{time} + $highlight_ua_hold_hour * 3600) > $time } @save_highlight_hashref_array;
    } elsif (!$modified_flag) {
        # タイムスタンプ更新・削除対象が見つからなかったため、404 Not Foundを返す
        close($json_log_fh);
        output_http_header($HTTP_STATUS_404_NOT_FOUND);
        exit();
    }

    # ログファイルを更新
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_highlight_hashref_array);

    # ログファイルクローズ
    close($json_log_fh);

    # 成功ステータスコードを返す
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # 正常終了
    $error_output_flg = 0;
}

# 不適切な値が送られてきたなど、エラー終了フラグが立ったままの場合は、400 Bad Requestを返す
if ($error_output_flg) {
    output_http_header($HTTP_STATUS_400_BAD_REQUEST);
    exit();
}

# HTTPステータスコード出力サブルーチン
# (ファイル上部で定義している変数をHTTPステータスコードとして引数に使用して下さい)
sub output_http_header {
    my ($http_status_code) = @_;
    print $http_status_code
            . "Cache-Control: private, no-store, no-cache, must-revalidate\n"
            . "Pragma: no-cache\n\n";
}
