package FirstCookie;
use strict;

use open IO => ':encoding(cp932)';

use Carp qw(confess croak);
use Encode qw();
use List::Util qw(min);
use POSIX qw(ceil);
use Scalar::Util qw(blessed);
use Time::Piece;
use Time::Seconds;

use List::MoreUtils qw(uniq);

use Matcher::Utils;

my Encode::Encoding $enc_cp932 = defined($main::enc_cp932) ? $main::enc_cp932 : Encode::find_encoding('cp932');
my Encode::Encoding $enc_utf8 = Encode::find_encoding('UTF-8');

# 種別定数定義
use constant {
    THREAD_CREATE => 1,
    RESPONSE      => 1 << 1
};

my $disable_setting_char = $enc_cp932->decode('▼');
my $restrict_time_char = $enc_cp932->decode('●');
my $additional_hosts_char = $enc_cp932->decode('★');
my $format_capture_regex = qr/^(\d{2}(?:0\d|1[0-2])(?:[0-2]\d|3[0-1])_(?:[01]\d|2[0-3])[0-5]\d)(?:$restrict_time_char(\d+)(?:$additional_hosts_char(.*))?)?$/;

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
}

# 初回Cookie発行日付フォーマットサブルーチン定義
sub format_issue_datetime {
    my $self = shift;
    if ((caller)[0] ne (caller(0))[0] || !defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance subroutine.');
    }

    my $first_access_time = $self->('TIME');
    my $now_time = $self->('NOW');

    if ($first_access_time->tzoffset == $now_time->tzoffset) {
        return substr($first_access_time->strftime('%Y%m%d_%H%M'), 2);
    } else {
        # Time::Piece 1.15以下のバグなどでタイムゾーンが異なる場合、オフセット秒を加算して表記上の時間を揃える
        my $offset = $now_time->tzoffset - $first_access_time->tzoffset;
        my $shifted_first_access_time = $first_access_time + $offset;
        return substr($shifted_first_access_time->strftime('%Y%m%d_%H%M'), 2);
    }
}

# 初回Cookie発行サブルーチン定義
sub issue_cookie {
    my $self = shift;
    if ((caller)[0] ne (caller(0))[0] || !defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance subroutine.');
    }

    # Cookie発行値作成
    my $issue_value = value($self);

    # Cookie発行
    my $raw_issue_value = $enc_utf8->encode($issue_value);
    $raw_issue_value =~ s/(\W)/'%' . unpack('H2', $1)/eg;
    $raw_issue_value =~ s/\s/+/g;
    if (length($raw_issue_value) <= 4093) {
        print 'Set-Cookie: ' . $self->('NAME') . "=$raw_issue_value; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
    } else {
        croak('Cookie value size limit exceeded. Can\'t set.');
    }
}

sub new {
    my $class = shift;
    my ($matcher_utils_instance,
        $setting_filepath,
        $time, $host, $useragent, $cookie_a, $user_id, $history_id, $is_private_browsing_mode,
        $cookie_current_dirpath, $firstpost_restrict_exempt_array_ref) = @_;
    arg_check(
        11,
        [
            'Matcher::Utils',
            '',
            '', '', '', 'UniqueCookie', '', '', '',
            '', 'ARRAY'
        ],
        @_
    );

    # 現在時刻のTime::Piece インスタンスを取得
    my $NOW_TIME_PIECE_INSTANCE = do {
        local $ENV{TZ} = "JST-9";
        my $tp = localtime($time);
        localtime($time - $tp->sec);
    };

    # CookieAの値を取得
    my $cookie_a_value = $cookie_a->value();

    my %self = (
        MATCHER_UTILS_INSTANCE    => $matcher_utils_instance,
        NAME                      => "WEB_PATIO_${cookie_current_dirpath}_FQ",
        NOW                       => $NOW_TIME_PIECE_INSTANCE,
        TIME                      => $NOW_TIME_PIECE_INSTANCE,
        COOKIE_A_VALUE            => $cookie_a_value,
        RESTRICTED                => 0,
        RESTRICT_HOUR             => 0,
        TITLE_MATCH_RESTRICT_HOUR => 0,
        ADD_JUDGE_HOSTS           => [],
        EXEMPT_USER               => 0
    );

    # Matcher::Utilsインスタンス取得
    my Matcher::Utils $mu = $matcher_utils_instance;

    # Cookie発行フラグ
    my $issue_cookie_flag = 1;

    # Cookie読み取り
    foreach my $cookie_set (split(/; */, $ENV{HTTP_COOKIE})) {
        my ($key, $value) = split(/=/, $cookie_set);
        if ($key eq $self{NAME}) {
            if ($value ne '') {
                my $urldecoded_value = $value;
                $urldecoded_value =~ s/\+/ /g;
                $urldecoded_value =~ s/%([0-9a-fA-F]{2})/pack('H2', $1)/eg;
                $urldecoded_value = $enc_utf8->decode($urldecoded_value);
                if ($urldecoded_value =~ $format_capture_regex) {
                    # 初回Cookie発行済で内容の更新を行わないので、
                    # 発行フラグをオフ
                    $issue_cookie_flag = 0;

                    # 日時取得
                    # (初回書き込み日時は初回CookieCookieにセットされている値を使用)
                    $self{TIME} = localtime(Time::Piece->strptime("20$1", '%Y%m%d_%H%M')); # %Yの先頭2桁が欠けているため、20??年として扱う
                    ## Time::Piece 1.15以下のバグなどでタイムゾーンが異なる場合、オフセット秒を減算して時間を揃える
                    if ($self{TIME}->tzoffset != $self{NOW}->tzoffset) {
                        my $offset = $self{TIME}->tzoffset - $self{NOW}->tzoffset;
                        $self{TIME} += $offset;
                    }

                    # 初回Cookieに制限時間を保持している場合は取得
                    if (defined($2)) {
                        $self{RESTRICT_HOUR} = int($2);
                    }

                    # 初回Cookieに追加判定ホストを保持している場合は取得
                    if (defined($3)) {
                        $self{ADD_JUDGE_HOSTS} = [uniq(grep { $_ ne '' } split(/,/, $3))];
                    }
                }
            }
            last;
        }
    }

    # 外部ファイルオープン
    open(my $setting_fh, '<', $setting_filepath) || croak("Open error: $setting_filepath");
    flock($setting_fh, 1) || croak("Lock error: $setting_filepath");
    $self{SETTING_FH} = $setting_fh;

    # ヘッダ行読み飛ばし
    <$setting_fh>;

    # 外部ファイルをパースし、有効な設定を読み込み
    my @thread_create_valid_settings;
    my @response_valid_settings;
    my @judge_hosts = ($host, @{$self{ADD_JUDGE_HOSTS}});
    while (my $line = <$setting_fh>) {
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @settings = split(/\^/, $line, - 1);
        if (scalar(@settings) != 8 || $settings[0] eq $disable_setting_char) {
            # 8列ではないログ行、もしくは、無効列に▼の列はスキップ
            next;
        }

        # 設定種別を取得
        my $type = int($settings[2]);
        if (!($type & (THREAD_CREATE | RESPONSE))) {
            # スレ作成orレス列の指定が正しくない設定行はスキップ
            next;
        }

        # 時間列のチェック
        $settings[5] = int($settings[5]);
        if ($settings[5] <= 0) {
            # 指定が正しくない場合はスキップ
            next;
        }

        # プライベートモードによるアクセスではない場合に、
        # プライベートモード列が1の設定行はスキップ
        if ($settings[6] eq '1' && !$is_private_browsing_mode) {
            next;
        }

        # ホストとUserAgentの一致判定
        my ($host_matched_flag, @match_host_settings);
        foreach my $judge_host (@judge_hosts) {
            my ($host_useragent_match_array_ref, $host_useragent_match_part_array_ref) =
                @{$mu->get_matched_host_useragent_and_whether_its_not_match(
                    $judge_host, $useragent, $settings[4], [ '*', undef() ], Matcher::Utils::UTF8_FLAG_FORCE_ON
                )};
            if (defined($host_useragent_match_array_ref)) {
                push(@match_host_settings, (grep { $_ ne '*' } @{${$host_useragent_match_part_array_ref}[0]}));
                $host_matched_flag ||= 1;
            }
        }
        if (!$host_matched_flag) {
            # 一致するホストがない場合はスキップ
            next;
        }
        @match_host_settings = uniq(@match_host_settings);

        # スレッド作成時/レス時別の設定配列・変数に有効な設定をセット
        if ($type & THREAD_CREATE) {
            push(@thread_create_valid_settings, [@settings, \@match_host_settings]);
        }
        if ($type & RESPONSE) {
            push(@response_valid_settings, [@settings, \@match_host_settings]);
        }
    }
    $self{THREAD_CREATE_VALID_SETTINGS_ARRAY_REF} = \@thread_create_valid_settings;
    $self{RESPONSE_VALID_SETTINGS_ARRAY_REF} = \@response_valid_settings;

    # 制限対象外ユーザー判定
    foreach my $exempt_set_str (@{$firstpost_restrict_exempt_array_ref}) {
        # 設定文字列分割して設定値を取得
        my @exempt_set = split(/:/, $exempt_set_str, 2);
        if (scalar(@exempt_set) < 1) {
            next;
        }

        # ホストとUserAgent or CookieA or 登録ID or 書込IDのいずれかで一致したかどうかのフラグ
        my $host_useragent_or_cookiea_userid_historyid_matched_flg;

        # ホスト・UserAgent一致判定
        my ($host_useragent_match_array_ref)
            = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $exempt_set[0], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
        $host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($host_useragent_match_array_ref);

        # CookieA or 登録ID or 書込ID一致判定
        if (!$host_useragent_or_cookiea_userid_historyid_matched_flg) {
            my ($cookiea_userid_historyid_match_array_ref)
                = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a_value, $user_id, $history_id, $exempt_set[1], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            $host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($cookiea_userid_historyid_match_array_ref);
        }

        # ホストとUserAgent or CookieA or 登録ID or 書込IDのいずれかで一致したため、
        # 対象外ユーザーフラグを立てる
        if ($host_useragent_or_cookiea_userid_historyid_matched_flg) {
            $self{EXEMPT_USER} = 1;
            last;
        }
    }

    # クロージャ定義
    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }

        # 1つ以上の引数が与えられた場合
        if (@_) {
            # キー名を最初の引数から取得
            my $field = shift;

            # キーが存在する場合
            if (exists($self{$field})) {
                # 値が引数として与えられた場合、セットする
                if (@_) {
                    $self{$field} = shift;
                }

                # キーに対応する値を返す
                return $self{$field};
            }
        }
    };

    # インスタンスを作成
    my $instance = bless $closure, $class;

    # 初回Cookie未発行の場合は発行する
    if ($issue_cookie_flag) {
        issue_cookie($instance);
    }

    return $instance;
}

sub judge_and_update_cookie {
    my $self = shift;
    my ($type, $thread_title) = @_;
    if (!defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance variable.');
    }
    if (!(($type & THREAD_CREATE) || ($type & RESPONSE))) {
        confess('invalid type has been set.');
    }

    # スレッド作成であるかどうかのフラッグ
    my $new_thread_flag = $type & THREAD_CREATE;

    # 初回Cookie更新発行フラッグ
    my $update_cookie_flag;

    # CookieAの値・文字数・日時数値表現を取得
    my $cookie_a_value = $self->('COOKIE_A_VALUE');
    my $cookie_a_length = length($cookie_a_value);
    my $cookie_a_issue_datetime_num;
    if (defined($self->('COOKIE_A_VALUE'))
        && $cookie_a_value =~ /^(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[0-1]))_.._((?:[01]\d|2[0-3])[0-5]\d)$/
    ) {
        $cookie_a_issue_datetime_num = int("$1$2");
    }

    # 参照する有効設定配列を決定
    my $valid_settings_array_ref
        = $new_thread_flag ? $self->('THREAD_CREATE_VALID_SETTINGS_ARRAY_REF') : $self->('RESPONSE_VALID_SETTINGS_ARRAY_REF');

    # Matcher::Utilsインスタンス取得
    my Matcher::Utils $mu = $self->('MATCHER_UTILS_INSTANCE');

    # 制限・除外対象判定
    foreach my $setting_array_ref (@{$valid_settings_array_ref}) {
        # 有効設定行を取得
        my @settings = @{$setting_array_ref};

        # 制限時間設定を取得
        my $restrict_hour_setting = $settings[5];

        # レス時にスレッド名一致判定
        if (!$new_thread_flag) {
            # スレッド名の指定がない場合はスキップ
            if ($settings[3] eq '') {
                next;
            }

            # 一致判定
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match(
                $thread_title, $settings[3], undef(), undef(), '*', Matcher::Utils::UTF8_FLAG_FORCE_ON
            )};
            if (!defined($title_match_array_ref)) {
                # 一致しなかった場合はスキップ
                next;
            } elsif (scalar(grep { $_ ne '*' } map { ${$_}[0] } @{$title_match_array_ref}) > 0
                && $restrict_hour_setting > $self->('TITLE_MATCH_RESTRICT_HOUR')
            ) {
                # 「*」以外でマッチしたスレッドタイトルの設定行のみの最長制限時間更新
                $self->('TITLE_MATCH_RESTRICT_HOUR', $restrict_hour_setting);
            }
        }

        # 制限対象フラグをセット
        $self->('RESTRICTED', 1);

        # 日付による除外列
        if (!$self->('EXEMPT_USER') && defined($cookie_a_value)
            && $settings[1] =~ /^\d{2}(\d{2})\/(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[0-1]) ([01]\d|2[0-3]):([0-5]\d)$/
        ) {
            if ($cookie_a_length == 14 && defined($cookie_a_issue_datetime_num)) {
                # 日付による除外列の指定日時 数値表現を作成
                my $reference_datetime_num = int("$1$2$3$4$5");

                # CookieA発行日時 が 日付による除外列の指定日時 未満である場合は除外対象
                if ($cookie_a_issue_datetime_num < $reference_datetime_num) {
                    $self->('EXEMPT_USER', 1);
                }
            } elsif ($cookie_a_length == 12) {
                # CookieAの桁数が12桁の場合は全て除外対象
                $self->('EXEMPT_USER', 1);
            }
        }

        # 最長制限時間更新
        if ($restrict_hour_setting > $self->('RESTRICT_HOUR')) {
            $self->('RESTRICT_HOUR', $restrict_hour_setting);
            $update_cookie_flag = 1;
        }

        # ホストとUserAgentが「*」以外で一致しているときは、
        # 追加判定ホストを追加更新する
        if (scalar(@{$settings[8]}) > 0) {
            my @current_add_judge_hosts = @{$self->('ADD_JUDGE_HOSTS')};
            my @updated_unique_add_judge_hosts = uniq(@current_add_judge_hosts, @{$settings[8]});
            if (scalar(@updated_unique_add_judge_hosts) != scalar(@current_add_judge_hosts)) {
                $self->('ADD_JUDGE_HOSTS', \@updated_unique_add_judge_hosts);
                $update_cookie_flag = 1;
            }
        }
    }

    # 初回Cookieの更新発行を必要に応じて行う
    if ($update_cookie_flag) {
        issue_cookie($self);
    }
}

sub get_left_hours_of_restriction {
    my ($self) = @_;
    if (!defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance variable.');
    }

    # 制限残り時間を計算して返す
    my $hours_of_restriction = get_hours_of_restriction($self);
    if ($self->('RESTRICTED') && !$self->('EXEMPT_USER') && $hours_of_restriction > 0) {
        # 初回アクセス日時+制限時間から現在日時を減算して、制限残り時間を算出
        # (制限解除日時の59秒までを制限時間に含めるので、制限時間+1分を加算してから、現在日時との差分を取る)
        my $left_time = ($self->('TIME') + ($hours_of_restriction * ONE_HOUR) + ONE_MINUTE) - $self->('NOW');
        my $left_hours = ceil($left_time->hours); # 残り時間を取得し、小数点以下を切り上げ (ex. 0.2h -> 1h)
        if ($left_hours >= 0) {
            # 0時間以上残っている場合はその時間を返す
            # (制限開始後最初の1時間は1時間1分の範囲を取るため、小数点以下切り上げで1時間多く表示されてしまうため、
            # 対策として、制限残り時間と制限時間のどちらか小さい方を使用する)
            return min($left_hours, $hours_of_restriction);
        } else {
            # マイナス時間は制限解除日時超過なので、0を返す
            return 0;
        }
    } else {
        # 制限対象外なので、0を返す
        return 0;
    }
}

sub get_first_access_datetime {
    my $self = shift;
    if (!defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance variable.');
    }

    # 初回Cookie発行日時をフォーマット
    my $value = format_issue_datetime($self);

    # CP932エンコードに変換して返す
    return $enc_cp932->encode($value);
}

sub get_hours_of_restriction {
    my $self = shift;
    if (!defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance variable.');
    }

    # 制限時間を返す
    # (スレッドタイトルで、*を除いた一致があった場合の最長制限時間を優先)
    return $self->('TITLE_MATCH_RESTRICT_HOUR') > 0 ? $self->('TITLE_MATCH_RESTRICT_HOUR') : $self->('RESTRICT_HOUR');
}

sub value {
    my $self = shift;
    my ($encode_flag) = @_;
    if (!defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance variable.');
    }

    # Cookie発行日時文字列作成
    my $value = format_issue_datetime($self);

    # 制限時間が設定されている時は、フラグ文字と制限時間情報を付加
    my $restrict_hour = $self->('RESTRICT_HOUR');
    if ($restrict_hour > 0) {
        $value .= $restrict_time_char . $restrict_hour;
    }

    # 追加判定ホストが存在する場合は、フラグ文字と追加判定ホスト文字列を付加
    my @unique_add_judge_hosts = uniq(@{$self->('ADD_JUDGE_HOSTS')});
    if (scalar(@unique_add_judge_hosts) > 0) {
        $value .= $additional_hosts_char . join(',', @unique_add_judge_hosts);
    }

    if ($encode_flag) {
        # CP932エンコードに変換して返す
        return $enc_cp932->encode($value);
    } else {
        # 内部エンコードのまま返す
        return $value;
    }
}

1;
