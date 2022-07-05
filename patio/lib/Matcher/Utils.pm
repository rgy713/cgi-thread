package Matcher::Utils;
use strict;
use warnings;

use encoding 'cp932';

use Carp qw(confess);
use Encode qw();
use JSON::XS;
use List::MoreUtils qw(all any pairwise uniq);
use Scalar::Util qw(blessed);
use Time::Piece;
use Time::Seconds;

use Matcher qw(match);

use Exporter 'import';
our @EXPORT    = qw();
our @EXPORT_OK = qw();

use constant {
    UTF8_FLAG_AS_IS_INPUT => 0,
    UTF8_FLAG_FORCE_OFF   => 1,
    UTF8_FLAG_FORCE_ON    => 1 << 1
};

sub new {
    my $class = shift;
    my ($time,
        $enc_cp932,
        $hiragana_katakana_normalize_mode,
        $variable,
        $trip_subroutine,
        $restrict_user_from_thread_page_target_log_path,
        $restrict_user_from_thread_page_target_hold_hour_1,
        $restrict_user_from_thread_page_target_hold_hour_2,
        $restrict_user_from_thread_page_target_hold_hour_3,
        $restrict_user_from_thread_page_target_hold_hour_4,
        $restrict_user_from_thread_page_target_hold_hour_5,
        $restrict_user_from_thread_page_target_hold_hour_6,
        $restrict_user_from_thread_page_target_hold_hour_7,
        $restrict_user_from_thread_page_by_time_range_target_log_path,
        $restrict_user_from_thread_page_by_time_range_target_hold_hour_1,
        $restrict_user_from_thread_page_by_time_range_target_hold_hour_2,
        $restrict_user_from_thread_page_by_time_range_target_hold_hour_3,
        $restrict_user_from_thread_page_by_time_range_target_hold_hour_4,
        $restrict_user_from_thread_page_by_time_range_enable_time_range,
        $in_thread_only_restrict_user_from_thread_page_target_log_path,
        $in_thread_only_restrict_user_from_thread_page_target_hold_hour
    ) = @_;

    if (!defined($hiragana_katakana_normalize_mode)
        || (   $hiragana_katakana_normalize_mode != Matcher::STRING_NORMALIZE_HIRAGANA_KATAKANA_CASE_SENSITIVE
            && $hiragana_katakana_normalize_mode != Matcher::STRING_NORMALIZE_HIRAGANA_KATAKANA_NOT_CASE_SENSITIVE )
        )
    {
        confess('$hiragana_katakana_normalize_mode must be set 0 or 1.');
    }

    if ( defined($variable) && ( !blessed($variable) || !$variable->isa('Matcher::Variable') ) ) {
        confess('$variable is not Matcher::Variable instance.');
    }

    my $now_time_piece_instance = do {
        local $ENV{TZ} = "JST-9";
        localtime($time);
    };

    my %self = (
        time                                                            => $time,
        enc_cp932                                                       => $enc_cp932,
        hiragana_katakana_normalize_mode                                => $hiragana_katakana_normalize_mode,
        variable                                                        => $variable,
        trip_subroutine                                                 => $trip_subroutine,
        restrict_user_from_thread_page_target_log_path                  => $restrict_user_from_thread_page_target_log_path,
        restrict_user_from_thread_page_target_hold_hour_1               => $restrict_user_from_thread_page_target_hold_hour_1,
        restrict_user_from_thread_page_target_hold_hour_2               => $restrict_user_from_thread_page_target_hold_hour_2,
        restrict_user_from_thread_page_target_hold_hour_3               => $restrict_user_from_thread_page_target_hold_hour_3,
        restrict_user_from_thread_page_target_hold_hour_4               => $restrict_user_from_thread_page_target_hold_hour_4,
        restrict_user_from_thread_page_target_hold_hour_5               => $restrict_user_from_thread_page_target_hold_hour_5,
        restrict_user_from_thread_page_target_hold_hour_6               => $restrict_user_from_thread_page_target_hold_hour_6,
        restrict_user_from_thread_page_target_hold_hour_7               => $restrict_user_from_thread_page_target_hold_hour_7,
        restrict_user_from_thread_page_by_time_range_target_log_path    => $restrict_user_from_thread_page_by_time_range_target_log_path,
        restrict_user_from_thread_page_by_time_range_target_hold_hour_1 => $restrict_user_from_thread_page_by_time_range_target_hold_hour_1,
        restrict_user_from_thread_page_by_time_range_target_hold_hour_2 => $restrict_user_from_thread_page_by_time_range_target_hold_hour_2,
        restrict_user_from_thread_page_by_time_range_target_hold_hour_3 => $restrict_user_from_thread_page_by_time_range_target_hold_hour_3,
        restrict_user_from_thread_page_by_time_range_target_hold_hour_4 => $restrict_user_from_thread_page_by_time_range_target_hold_hour_4,
        restrict_user_from_thread_page_by_time_range_enable_time_range  => $restrict_user_from_thread_page_by_time_range_enable_time_range,
        in_thread_only_restrict_user_from_thread_page_target_log_path   => $in_thread_only_restrict_user_from_thread_page_target_log_path,
        in_thread_only_restrict_user_from_thread_page_target_hold_hour  => $in_thread_only_restrict_user_from_thread_page_target_hold_hour,
        now_time_piece_instance                                         => $now_time_piece_instance
    );

    return bless \%self, $class;
}

# UTF8フラグを問わない
# 文字列の一致判定を行うサブルーチン
#
# 第1引数 : 判定対象文字列の配列リファレンス
# 第2引数 : 一致期待文字列の配列リファレンス
# 第3引数 : 一致設定文字列の接頭詞文字列の配列リファレンス (undefは何も付加しない) (['@ ', undef, undef, undef]など)
# 第4引数 : 全一致時の設定文字列置換文字列の配列リファレンス (undefは判定対象の文字列そのままとする) (['**', undef, undef, undef]など)
# 第5引数 : 返り値のUTF8フラグ
sub universal_match {
    my ( $self, $targets, $expects, $match_prefixes, $all_matches, $result_utf8mode ) = @_;

    # 判定対象および設定値のUTF8フラグを変換
    my $original_utf8flag;
    foreach my $str ( @{$targets}, @{$expects} ) {
        my $utf8flag;
        ( $str, $utf8flag ) = @{ $self->_convert_utf8_flag( $str, UTF8_FLAG_FORCE_ON ) };
        if ( !defined($original_utf8flag) ) {
            $original_utf8flag = $utf8flag;
        } elsif ( $result_utf8mode == UTF8_FLAG_AS_IS_INPUT && $utf8flag != $original_utf8flag ) {
            confess('Cannot use UTF8_FLAG_AS_IS_INPUT as $result_utf8mode. (some arguments strings are UTF8 flag different from others)');
        }
    }

    # 判定実施
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $variable                         = $self->{variable};
    my $results = match( $targets, $expects, $hiragana_katakana_normalize_mode, $match_prefixes, $all_matches, $variable );

    # 判定結果UTF8フラグ変換
    $results = $self->_convert_result_str_array_utf8_flag( $results, $original_utf8flag, $result_utf8mode );

    return $results;
}

# 与えられた文字列を「:」で区切って配列リファレンスで返します
# 期待する判定組み合わせ数以上に分割できる場合は、先頭の要素に余剰要素を結合します
#
# 第1引数: 文字列
# 第2引数: 期待する判定組み合わせ数
# 第3引数: 返り値のUTF8フラグ
sub number_of_elements_fixed_split {
    my ( $self, $set_str, $expect_elements_count, $result_utf8mode ) = @_;

    # 入力文字列のUTF8フラグを変換
    my $orig_utf8flag;
    ( $set_str, $orig_utf8flag ) = @{ $self->_convert_utf8_flag( $set_str, UTF8_FLAG_FORCE_ON ) };

    my @set_array = split( /:/, $set_str, -1 ); # 「:」で区切って配列とする
    my $elements_count = scalar(@set_array);    # 当初要素数を取得

    # 要素が期待数未満の時はから配列リファレンスを返す
    if ( $elements_count < $expect_elements_count ) {
        return [];
    }

    # 要素が期待数以上の時は、0～(余剰要素数)までのindexの要素について「:」で結合する
    if ( $elements_count > $expect_elements_count ) {
        my $last_concat_index = $elements_count - $expect_elements_count; # 結合する最後の要素のindex
        @set_array = ( join( ':', @set_array[ 0 .. ($last_concat_index) ] ), @set_array[ ( $last_concat_index + 1 ) .. $#set_array ] );
    }

    # 返り値のUTF8フラグを変換
    my $convert_to;
    if ( $result_utf8mode == UTF8_FLAG_AS_IS_INPUT ) {
        if ($orig_utf8flag) {
            $convert_to = UTF8_FLAG_FORCE_ON;
        } else {
            $convert_to = UTF8_FLAG_FORCE_OFF;
        }
    } else {
        $convert_to = $result_utf8mode;
    }
    @set_array = map { ${ $self->_convert_utf8_flag( $_, $convert_to ) }[0] } @set_array;

    return \@set_array;
}

# 現在時刻、もしくはTime::Pieceによる指定時刻が
# 指定書式文字列での時間範囲かどうかを判定するサブルーチン
#
# 第1引数: 時間範囲文字列
# 第2引数(オプション): Time::Pieceインスタンスの判定対象時刻
sub is_in_time_range {
    my ( $self, $time_range_str, $opt_time_to_check_time_piece_instance ) = @_;

    ($time_range_str) = @{ $self->_convert_utf8_flag( $time_range_str, UTF8_FLAG_FORCE_ON ) };

    local ( $1, $2 );
    if ( $time_range_str =~ /^((?:[0-1][0-9]|2[0-3])[0-5][0-9])-((?:[0-1][0-9]|2[0-3])[0-5][0-9])$/ ) {
        my $now_time_piece_instance = $self->{now_time_piece_instance};

        # 引数がある場合は指定日時、ない場合は現在日時のTime::Pieceインスタンスを使用する
        my $time_to_check = $opt_time_to_check_time_piece_instance || $now_time_piece_instance;

        # 時刻をセットしてTime::Pieceインスタンスを作成
        my $from = localtime( Time::Piece->strptime( $now_time_piece_instance->ymd . ' ' . $1, '%Y-%m-%d %H%M' ) );
        my $to   = localtime( Time::Piece->strptime( $now_time_piece_instance->ymd . ' ' . $2, '%Y-%m-%d %H%M' ) );
        ## Time::Piece 1.15以下のバグなどで、タイムゾーンが異なる場合、オフセット秒を加算して時間を揃える
        if ( $from->tzoffset != $time_to_check->tzoffset ) {
            my $offset = $from->tzoffset - $time_to_check->tzoffset;
            $from += $offset;
            $to   += $offset;
        }
        if ( $from > $to ) {

            # $fromよりも$toの時刻が前となっている場合、日付をまたいだ翌日の指定とする
            $to += ONE_DAY;
        }

        # $toは59秒までなので加算する
        $to += 59;

        # $time_to_checkが、$from以上 かつ $to以下(=範囲内の時刻)であるかどうかを返す
        return $from <= $time_to_check && $time_to_check <= $to;
    } else {

        # 書式が正しくないためundefを返す
        return;
    }
}

sub is_within_validity_period {
    my ( $self, $start_datetime, $effective_hour, $opt_time_to_check_time_piece_instance ) = @_;

    ($start_datetime) = @{ $self->_convert_utf8_flag( $start_datetime, UTF8_FLAG_FORCE_ON ) };
    ($effective_hour) = @{ $self->_convert_utf8_flag( $effective_hour, UTF8_FLAG_FORCE_ON ) };

    if (   $start_datetime !~ /^\d{4}\/(?:0[1-9]|1[0-2])\/(?:0[1-9]|[12][0-9]|3[01]) (?:[0-1][0-9]|2[0-3]):[0-5][0-9]$/
        || $effective_hour <= 0 )
    {
        return;
    }

    # 引数がある場合は指定日時、ない場合は現在日時のTime::Pieceインスタンスを使用する
    my $now_time_piece_instance = $self->{now_time_piece_instance};
    my $time_to_check = $opt_time_to_check_time_piece_instance || $now_time_piece_instance;

    # 対象範囲の始めと終わりのTime::Pieceインスタンスを作成
    my $from = localtime( Time::Piece->strptime( $start_datetime, '%Y/%m/%d %H:%M' ) );
    my $to = localtime( Time::Piece->strptime( $start_datetime, '%Y/%m/%d %H:%M' ) ) + ( ONE_HOUR * $effective_hour );

    # Time::Piece 1.15以下のバグなどで、タイムゾーンが異なる場合、オフセット秒を加算して時間を揃える
    if ( $from->tzoffset != $time_to_check->tzoffset ) {
        my $offset = $from->tzoffset - $time_to_check->tzoffset;
        $from += $offset;
        $to   += $offset;
    }

    # 有効時間範囲内かどうか判定して返す
    return $from <= $time_to_check && $to > $time_to_check;
}

# ホストとUserAgentの組み合わせの指定で一致した組み合わせを返すサブルーチン
#
# 第1引数: ホスト
# 第2引数: UserAgent (ホストのみでUserAgentの判定を行わない場合はundef)
# 第3引数: 一致判定を行う、ホストとUserAgentの組み合わせの設定文字列
# 第4引数: 全一致時の文字列を要素数2の配列リファレンスで指定(undefは判定対象の文字列そのままとする) (例 ['**', undef])
# 第5引数: 返り値のUTF8フラグ
#
# 返り値: 一致判定でいずれかに部分一致した場合は、[[(ホスト一致結果配列リファレンス), (UserAgent一致結果配列リファレンス)], 0]を返す
#         不一致判定でいずれも不一致の場合は、[[(不一致フラグ付ホスト設定値の配列リファレンス), (不一致フラグ付UserAgent設定値の配列リファレンス)], 1]を返す
#         いずれも一致/いずれかに不一致しなければ、[undef, 一致判定の場合は0/不一致判定の場合は1]を返す
sub get_matched_host_useragent_and_whether_its_not_match {
    my ( $self, $host, $useragent, $setting_str, $all_match_strs, $result_utf8mode ) = @_;

    if ( defined($all_match_strs) ) {
        if ( ref($all_match_strs) ne 'ARRAY' ) {
            confess('$all_match_strs is not ARRAY.');
        } elsif ( ( my $all_match_strs_len = scalar( @{$all_match_strs} ) ) != 2 ) {
            confess( sprintf( '$all_match_strs(len: %d) != 2', $all_match_strs_len ) );
        }
    } else {
        $all_match_strs = [ ( undef() ) x 2 ];
    }

    my @match_expect_settings;     # 一致判定設定値の配列
    my @not_match_expect_settings; # 不一致判定設定値の配列
    my @not_match_hosts;           # 不一致時に出力するホスト設定値の配列
    my @not_match_useragents;      # 不一致時に出力するUserAgent設定値の配列

    # $hostがIPアドレスに完全一致したかどうか
    my $ip_matched_flag = $host =~ /^(?:(?:2(?:[0-4]\d|5[0-5])|1\d{2}|[1-9]\d|\d)\.){3}(?:2(?:[0-4]\d|5[0-5])|1\d{2}|[1-9]\d|\d)$/;

    # 設定文字列のUTF8フラグを変換
    my $setting_str_utf8flag;
    ( $setting_str, $setting_str_utf8flag ) = @{ $self->_convert_utf8_flag( $setting_str, UTF8_FLAG_FORCE_ON ) };
    $all_match_strs = [ map { defined($_) ? ${ $self->_convert_utf8_flag( $_, UTF8_FLAG_FORCE_ON ) }[0] : $_ } @{$all_match_strs} ];

    # 変数展開
    $setting_str = $self->_extract_variable($setting_str);

    foreach my $host_useragent_set_str ( ( grep { $_ ne '' && $_ ne '-' } split( /●/, $setting_str ) ) ) {
        my ( $target_hosts_str, $target_useragents_str ) = split( /<>/, $host_useragent_set_str, 2 );
        if ( !defined($target_hosts_str) || $target_hosts_str eq '' ) {

            # 設定値のホストが定義されていない場合はスキップ
            next;
        }

        # ホストとUserAgentの組み合わせから判定項目を分割
        my @target_hosts = grep { $_ ne '' } ( split( /,/, $target_hosts_str ) );
        my @target_useragents;
        if ( defined($target_useragents_str) ) {
            @target_useragents = grep { $_ ne '' } ( split( /,/, $target_useragents_str ) );
        }

        # 判定対象のUserAgentの指定がないのに、設定値としてUserAgentが指定されているときはスキップ
        if ( !defined($useragent) && scalar(@target_useragents) >= 1 ) {
            next;
        }

        # 一致判定か不一致判定かを判別
        my $is_normal_match = all { substr( $_, 0, 1 ) ne '!' } ( @target_hosts, @target_useragents );
        my @orig_target_hosts_for_not_match;
        if ( !$is_normal_match ) {

            # 設定文字列が不一致判定の場合、不一致フラグ付き文字列に絞り、不一致フラグを取り除く
            @orig_target_hosts_for_not_match = grep { substr( $_, 0, 1 ) eq '!' } @target_hosts;
            @target_hosts = map { substr( $_, 1 ); } @target_hosts;
        }

        # 判定対象と判定設定のペアを作成
        my @target_settings_pairs = ( [ [ ($host) x scalar(@target_hosts) ], \@target_hosts ] );
        if ( ( my $target_useragents_length = scalar(@target_useragents) ) ) {
            push( @target_settings_pairs, [ [ ($useragent) x $target_useragents_length ], \@target_useragents ] );
        }

        # それぞれの設定値配列に追加
        if ($is_normal_match) {

            # 設定文字列が一致判定の場合
            push( @match_expect_settings, \@target_settings_pairs );
        } else {

            # 設定文字列が不一致判定の場合
            push( @not_match_expect_settings, \@target_settings_pairs );
            push( @not_match_hosts,           @orig_target_hosts_for_not_match );
            push( @not_match_useragents,      @target_useragents );
        }
    }

    # 判定組み合わせ作成
    my $is_not_match_int_flag = scalar(@not_match_expect_settings) > 0 ? 1 : 0;
    my $judge_combis = $is_not_match_int_flag ? \@not_match_expect_settings : \@match_expect_settings;

    # 判定実施
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my @setting_result                   = ( [], [] );
    my @target_result                    = ( [], [] );
COMBIS_LOOP:
    foreach my $combi_ref ( @{$judge_combis} ) {
        my @combi        = @{$combi_ref};
        my $combi_length = scalar(@combi);
        my ( @combi_result, @target_combi_result );

        # 判定対象ごとに一致判定を行う
    PAIR_LOOP: for ( my $i = 0; $i < $combi_length; $i++ ) { # 0: Host, 1: UserAgent
            my ( $targets, $settings ) = @{ $combi[$i] };
            my $current_all_match_strs = [ ( ${$all_match_strs}[$i] ) x scalar( @{$targets} ) ];

            # ホストの一致判定の場合、IPアドレス一致判定を行うかどうかを判定
            if ( $i == 0 ) {

                # 設定配列に$ipを含む要素indexをハッシュで取得
                my %ip_indexes = map { ${$settings}[$_] eq '$ip' ? ( $_ => 1 ) : (); } ( 0 .. $#{$settings} );

                # IPアドレス一致判定
                if ( scalar( keys(%ip_indexes) ) >= 1 ) {
                    if ($ip_matched_flag) {

                        # 一致結果として$ipをセット
                        push( @combi_result, ['$ip'] );
                        push( @target_combi_result, [$host] );
                        next PAIR_LOOP;
                    } else {

                        # IPアドレス一致しなかったため、
                        # $ipを除いた$targetsと$settingsにフィルタリングして一致判定を継続する
                        # ($current_all_match_strsは$targetsの要素数に合わせる)
                        $targets  = [ ( map { exists( $ip_indexes{$_} ) ? ${$targets}[$_]  : () } ( 0 .. $#{$targets} ) ) ];
                        $settings = [ ( map { exists( $ip_indexes{$_} ) ? ${$settings}[$_] : () } ( 0 .. $#{$settings} ) ) ];
                        $current_all_match_strs = [ ( ${$all_match_strs}[$i] ) x scalar( @{$targets} ) ];
                    }
                }
            }

            # 一致判定
            my $tmp_match_results = match( $targets, $settings, $hiragana_katakana_normalize_mode, undef(), $current_all_match_strs );

            # 不一致の場合は次のセット
            if ( !defined($tmp_match_results) ) {
                next COMBIS_LOOP;
            }

            # マッチした設定を取り出す
            push( @combi_result, [ grep { defined($_) } map { ${ ${$_}[0] }[0] } @{$tmp_match_results} ] );

            # マッチした対象を取り出す
            push( @target_combi_result, [ grep { defined($_) && $_ ne '' } map { ${ ${$_}[0] }[1] } @{$tmp_match_results} ] );
        }

        # 全体の結果配列に追加
        for ( my $i = 0; $i < 2; $i++ ) {
            if ( $i < $combi_length ) {
                push( @{ $setting_result[$i] }, @{ $combi_result[$i] } );
                push( @{ $target_result[$i] },  @{ $target_combi_result[$i] } );
            } elsif ( defined( ${$all_match_strs}[$i] ) ) {

                # UserAgentの一致判定を行わない判定対象/設定の組み合わせの場合
                # 一致設定配列にのみ、全一致文字列を追加する
                push( @{ $setting_result[$i] }, ${$all_match_strs}[$i] );
            }
        }

        if ($is_not_match_int_flag) {
            last COMBIS_LOOP;
        }
    }

    # 判定結果作成
    my ( $setting_result_array_ref, $target_result_array_ref );
    if ( !$is_not_match_int_flag ) {

        # 一致判定
        if ( scalar( @{ $setting_result[0] } ) > 0 ) {

            # 一致結果が得られた場合
            $setting_result_array_ref = \@setting_result;
            $target_result_array_ref  = \@target_result;
        }
    } else {

        # 不一致判定
        if ( scalar( @{ $setting_result[0] } ) == 0 ) {

            # 全てに不一致だった場合
            $setting_result_array_ref = [ \@not_match_hosts, \@not_match_useragents ]; # 不一致フラグ文字を先頭に付けた設定値の配列を返す
            $target_result_array_ref = [ [], [] ];                                     # 一致する判定対象はないので、いずれも空配列を返す
        }
    }

    # 判定結果UTF8フラグ変換
    my $convert_to;
    if ( $result_utf8mode == UTF8_FLAG_AS_IS_INPUT ) {
        $convert_to = $setting_str_utf8flag ? UTF8_FLAG_FORCE_ON : UTF8_FLAG_FORCE_OFF;
    } else {
        $convert_to = $result_utf8mode;
    }
    foreach my $result_array_ref ( $setting_result_array_ref, $target_result_array_ref ) {
        if ( !defined($result_array_ref) ) {
            next;
        }
        foreach my $array ( @{$result_array_ref} ) {
            foreach my $element ( @{$array} ) {
                if ( !defined($element) ) {
                    next;
                }
                ($element) = @{ $self->_convert_utf8_flag( $element, $convert_to ) };
            }
        }
    }

    return [ $setting_result_array_ref, $target_result_array_ref, $is_not_match_int_flag ];
}

# CookieA or 登録ID or 書込IDの完全一致判定を行うサブルーチン
#
# 第1引数: CookieA
# 第2引数: 登録ID
# 第3引数: 書込ID
# 第4引数: 一致判定を行う、CookieA or 登録ID or 書込IDの設定文字列
# 第5引数: 返り値のUTF8フラグ
#
# 返り値: 一致判定の場合、いずれかに完全一致したら[[(CookieA一致結果配列リファレンス), (登録ID一致結果配列リファレンス), (書込ID一致結果配列リファレンス)], 0]を返す
#         不一致判定の場合、全てに不一致だった場合[[[],[],[]], 1]を返す
#         いずれも一致/いずれかに不一致か不一致しなかった場合、[undef, 一致判定の場合は0/不一致判定の場合は1]を返す
sub get_matched_cookiea_userid_historyid_and_whether_its_not_match {
    my ( $self, $cookie_a, $user_id, $history_id, $setting_str, $result_utf8mode ) = @_;

    # 判定対象および設定値のUTF8フラグを変換
    my $setting_str_utf8flag;
    ( $setting_str, $setting_str_utf8flag ) = @{ $self->_convert_utf8_flag( $setting_str, UTF8_FLAG_FORCE_ON ) };
    foreach my $target ( $cookie_a, $user_id, $history_id ) {
        if ( !defined($target) ) {
            next;
        }

        my $target_utf8flag;
        ( $target, $target_utf8flag ) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        if ( $result_utf8mode == UTF8_FLAG_AS_IS_INPUT && $target_utf8flag != $setting_str_utf8flag ) {
            confess('Cannot use UTF8_FLAG_AS_IS_INPUT as $result_utf8mode. (some targets are UTF8 flag different from $setting_str)');
        }
    }

    # 判定結果UTF8フラグ確定
    my $convert_to;
    if ( $result_utf8mode == UTF8_FLAG_AS_IS_INPUT ) {
        if ($setting_str_utf8flag) {
            $convert_to = UTF8_FLAG_FORCE_ON;
        } else {
            $convert_to = UTF8_FLAG_FORCE_OFF;
        }
    } else {
        $convert_to = $result_utf8mode;
    }

    # 設定文字列を分割し、否定指定の設定がある場合はその設定のみに絞る
    my @judge_items = grep { $_ ne '' && $_ ne '-' } split( /,/, $setting_str );
    my @not_judge_items = map { substr( $_, 0, 1 ) eq '!' ? substr( $_, 1 ) : () } @judge_items;
    my $is_normal_match = scalar(@not_judge_items) == 0;
    if ( !$is_normal_match ) {
        @judge_items = @not_judge_items;
    }

    # 一致/不一致判定対象項目定義
    my @targets = ( $cookie_a, $user_id, $history_id );

    # 一致/不一致判定 (OR判定)
    my @result_array;
    foreach my $target (@targets) {
        if ( defined($target) && $target ne '' ) {
            push( @result_array, [ ( map { ${ $self->_convert_utf8_flag( $_, $convert_to ) }[0] } grep { $_ eq $target } @judge_items ) ] );
        } else {
            push( @result_array, [] );
        }
    }

    # 判定結果作成
    if ( any { scalar( @{$_} ) >= 1 } @result_array ) {

        # 完全一致する項目が1つ以上あった場合
        # (全てに完全一致 or 全てではないが不一致の項目がある場合も含む)
        if ($is_normal_match) {

            # 一致判定
            return [ \@result_array, 0 ];
        } else {

            # 不一致判定
            return [ undef(), 1 ];
        }
    } else {

        # 完全一致する項目が1つもなかった場合
        # (全てに不一致だった場合)
        if ($is_normal_match) {

            # 一致判定
            return [ undef(), 0 ];
        } else {

            # 不一致判定
            return [ \@result_array, 1 ]; # @result_array == [ ( [] ) x scalar(@targets) ] となっている
        }
    }
}

# スレッド名一致判定設定値との一致判定を行うサブルーチン
#
# 第1引数: 判定対象スレッド名 (内部エンコード変換後の値でも良い)
# 第2引数: スレッド名一致判定設定値
# 第3引数: 通常一致のみの判定とするかどうか (undefは、設定値に否定指定がある場合、否定一致のみの判定を行う)
# 第4引数: 一致時に先頭に付加する文字列を指定(undefは何も付加しない)
# 第5引数: 全一致時の文字列を指定(undefは判定対象の文字列そのままとする)
# 第6引数: 返り値のUTF8フラグ
#
# 返り値: 一致判定の場合、いずれかに一致したら[(一致結果配列リファレンス), 0]を返す
#         不一致判定の場合、全てに不一致だった場合[[], 1]を返す
#         全て一致しない/全てに不一致ではなかった場合、[undef, 一致判定の場合は0/不一致判定の場合は1]を返す
sub get_matched_thread_title_to_setting_and_whether_its_not_match {

    # 引数チェック・展開
    my ( $self, $thread_title, $setting_str, $normal_match_only_flg, $match_prefix_str, $wildcard_match_str, $result_utf8mode ) = @_;
    if ( $thread_title eq '' || $setting_str eq '' ) {
        return [ undef(), 0 ];
    }

    # 必要に応じてスレッド名を内部エンコードに変換
    my $thread_title_utf8flag;
    ( $thread_title, $thread_title_utf8flag ) = @{ $self->_convert_utf8_flag( $thread_title, UTF8_FLAG_FORCE_ON ) };

    # 設定文字列を必要に応じて内部エンコードに変換
    my $setting_str_utf8flag;
    ( $setting_str, $setting_str_utf8flag ) = @{ $self->_convert_utf8_flag( $setting_str, UTF8_FLAG_FORCE_ON ) };
    if ( defined($match_prefix_str) ) {
        ($match_prefix_str) = @{ $self->_convert_utf8_flag( $match_prefix_str, UTF8_FLAG_FORCE_ON ) };
    }
    if ( defined($wildcard_match_str) ) {
        ($wildcard_match_str) = @{ $self->_convert_utf8_flag( $wildcard_match_str, UTF8_FLAG_FORCE_ON ) };
    }

    if ( $thread_title_utf8flag != $setting_str_utf8flag && $result_utf8mode == UTF8_FLAG_AS_IS_INPUT ) {
        confess('Cannot use UTF8_FLAG_AS_IS_INPUT as $result_utf8mode. ($thread_title_utf8flag != $setting_str_utf8flag)');
    }

    # 変数展開
    my $variable_extracted_setting_str = $self->_extract_variable($setting_str);

    # 設定文字列を分割し、条件優先フラグに応じて否定指定の設定がある場合はその設定のみに絞る
    my @judge_items = grep { $_ ne '' } @{ Matcher::_expect_split( $variable_extracted_setting_str, 0, ',' ) };
    my $is_normal_match = 1;
    if ($normal_match_only_flg) {

        # 通常一致条件のみ
        @judge_items = grep { substr( $_, 0, 1 ) ne '!' } @judge_items;
    } else {

        # 否定一致条件優先
        my @not_judge_items = map { substr( $_, 0, 1 ) eq '!' ? substr( $_, 1 ) : () } @judge_items;
        $is_normal_match = scalar(@not_judge_items) == 0;
        if ( !$is_normal_match ) {
            @judge_items = @not_judge_items;
        }
    }

    # OR条件を再結合して、通常の一致判定を行う
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $rejoined_setting_str = join( ',', @judge_items );
    my $matched_title_array_ref
        = match( [$thread_title], [$rejoined_setting_str], $hiragana_katakana_normalize_mode, [$match_prefix_str], [$wildcard_match_str] );

    # 判定結果を作成
    if ( defined($matched_title_array_ref) ) {

        # 一部または全部が一致していた場合
        if ($is_normal_match) {

            # 一致判定

            # 一致結果のUTF8フラグを変換
            $self->_convert_result_str_array_utf8_flag( $matched_title_array_ref, $thread_title_utf8flag, $result_utf8mode );

            # 結果配列の次元を削減して返す (一致項目はもとより1つなので)
            return [ ${$matched_title_array_ref}[0], 0 ];
        } else {

            # 不一致判定
            return [ undef(), 1 ];
        }
    } else {

        # 全てに不一致だった場合
        if ($is_normal_match) {

            # 一致判定
            return [ undef(), 0 ];
        } else {

            # 不一致判定
            return [ [], 1 ];
        }
    }
}

# 名前欄一致判定設定値との一致判定を行うサブルーチン
# 第1引数 : 判定要素別の判定対象文字列
# 第2引数 : 名前一致判定組み合わせ設定値の配列リファレンス
# 第3引数 : 返り値のUTF8フラグ
sub get_matched_name_to_setting {

    # 引数チェック・展開
    my ( $self, $raw_name, $setting_str, $result_utf8mode ) = @_;
    if ( $raw_name eq '' || $setting_str eq '' ) {
        return;
    }

    if ( $setting_str eq '*' ) {
        return ['*'];
    }

    # 名前を内部エンコードに変換
    my ( $utf8flagged_raw_name, $raw_name_utf8flag ) = @{ $self->_convert_utf8_flag( $raw_name, UTF8_FLAG_FORCE_ON ) };
    my ($utf8notflagged_raw_name) = @{ $self->_convert_utf8_flag( $raw_name, UTF8_FLAG_FORCE_OFF ) };

    # 設定文字列を内部エンコードに変換
    my $setting_str_utf8flag;
    ( $setting_str, $setting_str_utf8flag ) = @{ $self->_convert_utf8_flag( $setting_str, UTF8_FLAG_FORCE_ON ) };

    if ( $raw_name_utf8flag != $setting_str_utf8flag && $result_utf8mode == UTF8_FLAG_AS_IS_INPUT ) {
        confess('Cannot use UTF8_FLAG_AS_IS_INPUT as $result_utf8mode. ($raw_name_utf8flag != $setting_str_utf8flag)');
    }

    # トリップ変換サブルーチンを取得
    my $trip_subroutine = $self->{trip_subroutine};

    # トリップ変換後の名前を生成し、内部エンコードに変換
    my ($trip_converted_name) = @{ $self->_convert_utf8_flag( $trip_subroutine->($utf8notflagged_raw_name), UTF8_FLAG_FORCE_ON ) };

    # 判定を行う名前決定 内部サブルーチン
    my $get_match_target_name_from_setting_str = sub {
        my ($set_str) = @_;
        my @ret_targets;

        # 設定文字列にトリップシード/トリップ識別子を含むかどうか
        my $trip_seed_flag = index( $set_str, '#' ) != -1;
        my $trip_flag      = index( $set_str, '◆' ) != -1;

        # 設定値にトリップシードを含む指定があるため、
        # 名前判定でも含めて判定を行う
        if ($trip_seed_flag) {

            # トリップ変換前の名前を使用 (トリップシード部分含む)
            push( @ret_targets, $utf8flagged_raw_name );
        }

        # 設定値にトリップを含む指定があるため、
        # 名前判定でも含めて判定を行う
        if ($trip_flag) {

            # トリップ変換後の名前を使用 (トリップ部分含む)
            push( @ret_targets, $trip_converted_name );
        }

        # どちらの指定もない場合
        if ( !$trip_flag && !$trip_seed_flag ) {

            # 通常の名前部分のみの判定
            # トリップ変換前の名前を使用 (トリップシード/トリップ部分含まず)
            push( @ret_targets, ( split( /#|◆/, $utf8flagged_raw_name, 2 ) )[0] );
        }

        return \@ret_targets;
    };

    # 変数展開
    my $variable_extracted_setting_str = $self->_extract_variable($setting_str);

    # 設定文字列をOR条件別に分割
    my @or_settings = grep { $_ ne '' } @{ Matcher::_expect_split( $variable_extracted_setting_str, 0, ',' ) };

    # 判定対象・設定の組み合わせを作成
    my ( @targets, @expects );
    foreach my $or_setting (@or_settings) {
        my @current_targets = @{ $get_match_target_name_from_setting_str->($or_setting) };
        push( @targets, @current_targets );
        push( @expects, ( ($or_setting) x scalar(@current_targets) ) );
    }

    # 判定実施
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $match_results = match( \@targets, \@expects, $hiragana_katakana_normalize_mode, undef(), undef(), $self->{variable} );
    if ( !defined($match_results) ) {
        return;
    }

    # 一致結果のUTF8フラグを変換
    $match_results = $self->_convert_result_str_array_utf8_flag( $match_results, $raw_name_utf8flag, $result_utf8mode );

    # 一致結果のうち、一致設定のみを取り出し、ユニーク化して返す
    my @results;
    foreach my $targets_array ( @{$match_results} ) {
        foreach my $or_array ( @{$targets_array} ) {
            my $match_setting = ${$or_array}[0];
            push( @results, $match_setting );
        }
    }
    @results = uniq(@results);
    return \@results;
}

# スレッド画面からユーザーを制限する機能の一致判定を行うサブルーチン
#
# 第1引数: CookieA
# 第2引数: 登録ID
# 第3引数: 書込ID
# 第4引数: ホスト
sub is_restricted_user_from_thread_page {
    my ( $self, $cookie_a, $user_id, $history_id, $host ) = @_;

    # 判定対象のUTF8フラグを変換
    foreach my $target ( $cookie_a, $user_id, $history_id, $host ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # 設定など取得
    my $time                                              = $self->{time};
    my $restrict_user_from_thread_page_target_log_path    = $self->{restrict_user_from_thread_page_target_log_path};
    my $restrict_user_from_thread_page_target_hold_hour_1 = $self->{restrict_user_from_thread_page_target_hold_hour_1};
    my $restrict_user_from_thread_page_target_hold_hour_2 = $self->{restrict_user_from_thread_page_target_hold_hour_2};
    my $restrict_user_from_thread_page_target_hold_hour_3 = $self->{restrict_user_from_thread_page_target_hold_hour_3};
    my $restrict_user_from_thread_page_target_hold_hour_4 = $self->{restrict_user_from_thread_page_target_hold_hour_4};
    my $restrict_user_from_thread_page_target_hold_hour_5 = $self->{restrict_user_from_thread_page_target_hold_hour_5};
    my $restrict_user_from_thread_page_target_hold_hour_6 = $self->{restrict_user_from_thread_page_target_hold_hour_6};
    my $restrict_user_from_thread_page_target_hold_hour_7 = $self->{restrict_user_from_thread_page_target_hold_hour_7};

    # ログファイルサイズから内容がないと判断される場合には、設定に一致しなかったものとして返す
    if ( -s $restrict_user_from_thread_page_target_log_path <= 2 ) {
        return;
    }

    # ログパース処理
    my @restrict_user_settings_array;
    {
        # ログファイルオープン (失敗時は、設定に一致しなかったものとして返す)
        open( my $json_log_fh, '<:utf8', $restrict_user_from_thread_page_target_log_path ) || return;
        flock( $json_log_fh, 1 ) || return;

        # ログファイル読み込み
        seek( $json_log_fh, 0, 0 );
        local $/;
        my $json_log_contents = <$json_log_fh>;
        close($json_log_fh);

        # JSONパースを行う
        eval {
            my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
            if ( ref($json_parsed_ref) ne 'ARRAY' ) {

                # JSONのルートが配列でなく、想定と異なる構造の場合、
                # 設定に一致しなかったものとしてエラーを返す
                die();
            }
            @restrict_user_settings_array = @{$json_parsed_ref};
        };
        if ($@) {

            # JSONパースに失敗した (内容に異常がある)場合、
            # 設定に一致しなかったものとして返す
            return;
        }
    }

    # パースした配列の制限設定ハッシュのうち、無効な制限設定を取り除く
    @restrict_user_settings_array = grep {
               ref($_) eq 'HASH'
            && exists( $_->{type} )
            && ( $_->{type} == 0
            || ( $_->{type} == 1 && ( ( $_->{time} + $restrict_user_from_thread_page_target_hold_hour_1 * 3600 ) >= $time ) )
            || ( $_->{type} == 2 && ( ( $_->{time} + $restrict_user_from_thread_page_target_hold_hour_2 * 3600 ) >= $time ) )
            || ( $_->{type} == 3 && ( ( $_->{time} + $restrict_user_from_thread_page_target_hold_hour_3 * 3600 ) >= $time ) )
            || ( $_->{type} == 4 && ( ( $_->{time} + $restrict_user_from_thread_page_target_hold_hour_4 * 3600 ) >= $time ) )
            || ( $_->{type} == 5 && ( ( $_->{time} + $restrict_user_from_thread_page_target_hold_hour_5 * 3600 ) >= $time ) )
            || ( $_->{type} == 6 && ( ( $_->{time} + $restrict_user_from_thread_page_target_hold_hour_6 * 3600 ) >= $time ) )
            || ( $_->{type} == 7 && ( ( $_->{time} + $restrict_user_from_thread_page_target_hold_hour_7 * 3600 ) >= $time ) ) )
            && exists( $_->{time} )
            && $_->{time} >= 0
            && ( ( defined( $_->{cookie_a} ) && $_->{cookie_a} ne '' )
            || ( defined( $_->{history_id} ) && $_->{history_id} ne '' )
            || ( defined( $_->{host} )       && $_->{host} ne '' )
            || ( defined( $_->{user_id} )    && $_->{user_id} ne '' ) )
    } @restrict_user_settings_array;

    # 一致判定
    foreach my $setting_ref (@restrict_user_settings_array) {

        # ホスト判定
        if (   defined( $setting_ref->{host} )
            && $setting_ref->{host} ne ''
            && defined(
                ${  $self->get_matched_host_useragent_and_whether_its_not_match( $host, undef(), $setting_ref->{host}, undef(),
                        UTF8_FLAG_FORCE_ON )
                }[0]
            )
            )
        {
            return 1;
        }

        # CookieA or 登録ID or 書込ID判定
        if (   ( defined( $setting_ref->{cookie_a} ) && $setting_ref->{cookie_a} ne '' )
            || ( defined( $setting_ref->{user_id} ) && $setting_ref->{user_id} ne '' )
            || ( defined( $setting_ref->{history_id} ) && $setting_ref->{history_id} ne '' ) )
        {
            my $match_str
                = join( ',', grep { $_ ne '' } ( $setting_ref->{cookie_a}, $setting_ref->{user_id}, $setting_ref->{history_id} ) );
            if ($match_str ne ''
                && defined(
                    ${  $self->get_matched_cookiea_userid_historyid_and_whether_its_not_match( $cookie_a, $user_id, $history_id,
                            $match_str, UTF8_FLAG_FORCE_ON )
                    }[0]
                )
                )
            {
                return 1;
            }
        }
    }

    # すべて一致しなかった
    return;
}

# スレッド画面からユーザを時間制限する機能の一致判定を行うサブルーチン
#
# 第1引数: CookieA
# 第2引数: 登録ID
# 第3引数: 書込ID
# 第4引数: ホスト
sub is_restricted_user_from_thread_page_by_time_range {
    my ( $self, $cookie_a, $user_id, $history_id, $host ) = @_;

    # 判定対象のUTF8フラグを変換
    foreach my $target ( $cookie_a, $user_id, $history_id, $host ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # 設定など取得
    my $time = $self->{time};
    my $restrict_user_from_thread_page_by_time_range_target_log_path
        = $self->{restrict_user_from_thread_page_by_time_range_target_log_path};
    my $restrict_user_from_thread_page_by_time_range_target_hold_hour_1
        = $self->{restrict_user_from_thread_page_by_time_range_target_hold_hour_1};
    my $restrict_user_from_thread_page_by_time_range_target_hold_hour_2
        = $self->{restrict_user_from_thread_page_by_time_range_target_hold_hour_2};
    my $restrict_user_from_thread_page_by_time_range_target_hold_hour_3
        = $self->{restrict_user_from_thread_page_by_time_range_target_hold_hour_3};
    my $restrict_user_from_thread_page_by_time_range_target_hold_hour_4
        = $self->{restrict_user_from_thread_page_by_time_range_target_hold_hour_4};
    my $restrict_user_from_thread_page_by_time_range_enable_time_range
        = $self->{restrict_user_from_thread_page_by_time_range_enable_time_range};

    # 制限時間内であるかどうか判定
    if (   !defined($restrict_user_from_thread_page_by_time_range_enable_time_range)
        || !$self->is_in_time_range($restrict_user_from_thread_page_by_time_range_enable_time_range) )
    {
        # 指定がない場合、もしくは、時間外の場合は設定に一致しなかったものとして返す
        return;
    }

    # ログファイルサイズから内容がないと判断される場合には、設定に一致しなかったものとして返す
    if ( -s $restrict_user_from_thread_page_by_time_range_target_log_path <= 2 ) {
        return;
    }

    # ログパース処理
    my @restrict_user_settings_array;
    {
        # ログファイルオープン (失敗時は、設定に一致しなかったものとして返す)
        open( my $json_log_fh, '<:utf8', $restrict_user_from_thread_page_by_time_range_target_log_path ) || return;
        flock( $json_log_fh, 1 ) || return;

        # ログファイル読み込み
        seek( $json_log_fh, 0, 0 );
        local $/;
        my $json_log_contents = <$json_log_fh>;
        close($json_log_fh);

        # JSONパースを行う
        eval {
            my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
            if ( ref($json_parsed_ref) ne 'ARRAY' ) {

                # JSONのルートが配列でなく、想定と異なる構造の場合、
                # 設定に一致しなかったものとしてエラーを返す
                die();
            }
            @restrict_user_settings_array = @{$json_parsed_ref};
        };
        if ($@) {

            # JSONパースに失敗した (内容に異常がある)場合、
            # 設定に一致しなかったものとして返す
            return;
        }
    }

    # パースした配列の制限設定ハッシュのうち、無効な制限設定を取り除く
    @restrict_user_settings_array = grep {
               ref($_) eq 'HASH'
            && exists( $_->{type} )
            && ( $_->{type} == 0
            || ( $_->{type} == 1 && ( ( $_->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_1 * 3600 ) >= $time ) )
            || ( $_->{type} == 2 && ( ( $_->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_2 * 3600 ) >= $time ) )
            || ( $_->{type} == 3 && ( ( $_->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_3 * 3600 ) >= $time ) )
            || ( $_->{type} == 4 && ( ( $_->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_4 * 3600 ) >= $time ) )
            )
            && exists( $_->{time} )
            && $_->{time} >= 0
            && ( ( defined( $_->{cookie_a} ) && $_->{cookie_a} ne '' )
            || ( defined( $_->{history_id} ) && $_->{history_id} ne '' )
            || ( defined( $_->{host} )       && $_->{host} ne '' )
            || ( defined( $_->{user_id} )    && $_->{user_id} ne '' ) )
    } @restrict_user_settings_array;

    # 一致判定
    foreach my $setting_ref (@restrict_user_settings_array) {

        # ホスト判定
        if (   defined( $setting_ref->{host} )
            && $setting_ref->{host} ne ''
            && defined(
                ${  $self->get_matched_host_useragent_and_whether_its_not_match( $host, undef(), $setting_ref->{host}, undef(),
                        UTF8_FLAG_FORCE_ON )
                }[0]
            )
            )
        {
            return 1;
        }

        # CookieA or 登録ID or 書込ID判定
        if (   ( defined( $setting_ref->{cookie_a} ) && $setting_ref->{cookie_a} ne '' )
            || ( defined( $setting_ref->{user_id} ) && $setting_ref->{user_id} ne '' )
            || ( defined( $setting_ref->{history_id} ) && $setting_ref->{history_id} ne '' ) )
        {
            my $match_str
                = join( ',', grep { $_ ne '' } ( $setting_ref->{cookie_a}, $setting_ref->{user_id}, $setting_ref->{history_id} ) );
            if ($match_str ne ''
                && defined(
                    ${  $self->get_matched_cookiea_userid_historyid_and_whether_its_not_match( $cookie_a, $user_id, $history_id,
                            $match_str, UTF8_FLAG_FORCE_ON )
                    }[0]
                )
                )
            {
                return 1;
            }
        }
    }

    # すべて一致しなかった
    return;
}

# スレッド画面からユーザーを制限する機能 (そのスレのみ)の一致判定を行うサブルーチン
#
# 第1引数: スレッドNo
# 第2引数: CookieA
# 第3引数: 登録ID
# 第4引数: 書込ID
# 第5引数: ホスト
sub is_in_thread_only_restricted_user_from_thread_page {
    my ( $self, $thread_number, $cookie_a, $user_id, $history_id, $host ) = @_;

    # 判定対象のUTF8フラグを変換
    foreach my $target ( $cookie_a, $user_id, $history_id, $host ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # 設定など取得
    my $time = $self->{time};
    my $in_thread_only_restrict_user_from_thread_page_target_log_path
        = $self->{in_thread_only_restrict_user_from_thread_page_target_log_path};
    my $in_thread_only_restrict_user_from_thread_page_target_hold_hour
        = $self->{in_thread_only_restrict_user_from_thread_page_target_hold_hour};

    # ログファイルサイズから内容がないと判断される場合には、設定に一致しなかったものとして返す
    if ( -s $in_thread_only_restrict_user_from_thread_page_target_log_path <= 2 ) {
        return;
    }

    # ログパース処理
    my %restrict_user_settings_thread_hash;
    {
        # ログファイルオープン (失敗時は、設定に一致しなかったものとして返す)
        open( my $json_log_fh, '<:utf8', $in_thread_only_restrict_user_from_thread_page_target_log_path ) || return;
        flock( $json_log_fh, 1 ) || return;

        # ログファイル読み込み
        seek( $json_log_fh, 0, 0 );
        local $/;
        my $json_log_contents = <$json_log_fh>;
        close($json_log_fh);

        # JSONパースを行う
        eval {
            my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
            if ( ref($json_parsed_ref) ne 'HASH' ) {

                # JSONのルートが連想配列でなく、想定と異なる構造の場合、
                # 設定に一致しなかったものとして返す
                die();
            }
            %restrict_user_settings_thread_hash = %{$json_parsed_ref};
        };
        if ($@) {

            # JSONパースに失敗した (内容に異常がある)場合、
            # 設定に一致しなかったものとして返す
            return;
        }
    }

    # 表示するスレッドNoのキーが含まれていない、
    # もしくは、値が配列ではない場合は、設定に一致していないので返す
    if (  !exists( $restrict_user_settings_thread_hash{$thread_number} )
        || ref( $restrict_user_settings_thread_hash{$thread_number} ) ne 'ARRAY' )
    {
        return;
    }

    # このスレッドを対象とした制限設定配列を取得し、無効な制限設定を取り除く
    my @restrict_user_settings_array = grep {
               ref($_) eq 'HASH'
            && exists( $_->{time} )
            && $_->{time} >= 0
            && ( $_->{time} + $in_thread_only_restrict_user_from_thread_page_target_hold_hour * 3600 ) >= $time
            && ( ( defined( $_->{cookie_a} ) && $_->{cookie_a} ne '' )
            || ( defined( $_->{history_id} ) && $_->{history_id} ne '' )
            || ( defined( $_->{host} )       && $_->{host} ne '' )
            || ( defined( $_->{user_id} )    && $_->{user_id} ne '' ) )
    } @{ $restrict_user_settings_thread_hash{$thread_number} };

    # 一致判定
    foreach my $setting_ref (@restrict_user_settings_array) {

        # ホスト判定
        if (   defined( $setting_ref->{host} )
            && $setting_ref->{host} ne ''
            && defined(
                ${  $self->get_matched_host_useragent_and_whether_its_not_match( $host, undef(), $setting_ref->{host}, undef(),
                        UTF8_FLAG_FORCE_ON )
                }[0]
            )
            )
        {
            return 1;
        }

        # CookieA or 登録ID or 書込ID判定
        if (   ( defined( $setting_ref->{cookie_a} ) && $setting_ref->{cookie_a} ne '' )
            || ( defined( $setting_ref->{user_id} ) && $setting_ref->{user_id} ne '' )
            || ( defined( $setting_ref->{history_id} ) && $setting_ref->{history_id} ne '' ) )
        {
            my $match_str
                = join( ',', grep { $_ ne '' } ( $setting_ref->{cookie_a}, $setting_ref->{user_id}, $setting_ref->{history_id} ) );
            if ($match_str ne ''
                && defined(
                    ${  $self->get_matched_cookiea_userid_historyid_and_whether_its_not_match( $cookie_a, $user_id, $history_id,
                            $match_str, UTF8_FLAG_FORCE_ON )
                    }[0]
                )
                )
            {
                return 1;
            }
        }
    }

    # すべて一致しなかった
    return;
}

# ホストなどによる画像アップロードの無効の一致判定を行うサブルーチン
#
# 第1引数: スレッド名 (新規スレッド作成時はundefを指定)
# 第2引数: ホスト
# 第3引数: UserAgent(_を-に置き換え、,:を除く)
# 第4引数: CookieA
# 第5引数: 登録ID
# 第6引数: 書込ID
# 第7引数: プライベートブラウジングモードであるかどうか
# 第8引数: ホストなどによる画像アップロードの無効 設定配列への配列リファレンス
sub is_disable_upload_img {
    my ( $self, $thread_title, $host, $useragent, $cookie_a, $user_id, $history_id, $is_private, $restricted_settings_array_ref ) = @_;
    if ( ref($restricted_settings_array_ref) ne 'ARRAY' ) {
        return;
    }

    # 判定対象のUTF8フラグを変換
    foreach my $target ( $thread_title, $host, $useragent, $cookie_a, $user_id, $history_id ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # Matcher::matchサブルーチン呼び出しに必要な
    # ひらがな/カタカナの大/小文字区別モード値・Variableインスタンスを取得
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $variable                         = $self->{variable};

    foreach my $restricted_set_str ( @{$restricted_settings_array_ref} ) {

        # 設定文字列のUTF8フラグを変換し、「:」で区切って配列とする
        ($restricted_set_str) = @{ $self->_convert_utf8_flag( $restricted_set_str, UTF8_FLAG_FORCE_ON ) };
        my @restricted_set_array = @{ $self->number_of_elements_fixed_split( $restricted_set_str, 5, UTF8_FLAG_AS_IS_INPUT ) };
        if ( scalar(@restricted_set_array) != 5 ) {

            # 要素数が正しくないため、次のループへ
            next;
        }

        # プライベートブラウジングモードの判定
        if ( $restricted_set_array[3] eq '1' && !$is_private ) {

            # プライベートブラウジングモードではなかったので次のループへ
            next;
        }

        # 判定無視項目の設定
        foreach my $i ( 1, 2 ) {
            if ( $restricted_set_array[$i] eq '-' ) {

                # 「-」のみの場合に「」(空)に置き換える
                $restricted_set_array[$i] = '';
            }
        }

        # ホストとUserAgent・CookieA or 登録ID or 書込IDの両方が空値の場合はスキップ
        if ( $restricted_set_array[1] eq '' && $restricted_set_array[2] eq '' ) {
            next;
        }

        # スレッド名判定
        if ( defined($thread_title) ) {

            # レス投稿時
            if (!defined(
                    match( [$thread_title], [ $restricted_set_array[0] ], $hiragana_katakana_normalize_mode, undef(), undef(), $variable )
                )
                )
            {

                # 一致しないときは次のループへ
                next;
            }
        } else {

            # 新規スレッド作成時
            if ( $restricted_set_array[0] ne '*' ) {

                # 「*」の指定がないときは次のループへ
                next;
            }
        }

        # ホストとUserAgentの組み合わせ判定
        if ( $restricted_set_array[1] ne '' ) {
            my ($host_useragent_match_array) = @{
                $self->get_matched_host_useragent_and_whether_its_not_match( $host, $useragent, $restricted_set_array[1],
                    undef(), UTF8_FLAG_FORCE_ON )
            };
            if ( defined($host_useragent_match_array) ) {
                return 1;
            }
        }

        # CookieA or 登録ID or 書込ID判定
        if ( $restricted_set_array[2] ne '' ) {
            my ($cookiea_userid_historyid_match_array) = @{
                $self->get_matched_cookiea_userid_historyid_and_whether_its_not_match( $cookie_a, $user_id, $history_id,
                    $restricted_set_array[2],
                    UTF8_FLAG_FORCE_ON )
            };
            if ( defined($cookiea_userid_historyid_match_array) ) {
                return 1;
            }
        }
    }

    # いずれの設定にも一致しなかった
    return;
}

# ホストなどによるageの無効の一致判定を行うサブルーチン
#
# 第1引数: スレッド名
# 第2引数: ホスト
# 第3引数: UserAgent(_を-に置き換え、,:を除く)
# 第4引数: CookieA
# 第5引数: 登録ID
# 第6引数: 書込ID
# 第7引数: プライベートブラウジングモードであるかどうか
# 第8引数: ホストなどによるageの無効 設定配列への配列リファレンス
sub is_disable_age {
    my ( $self, $thread_title, $host, $useragent, $cookie_a, $user_id, $history_id, $is_private, $restricted_settings_array_ref ) = @_;
    if ( ref($restricted_settings_array_ref) ne 'ARRAY' ) {
        return;
    }

    # 判定対象のUTF8フラグを変換
    foreach my $target ( $thread_title, $host, $useragent, $cookie_a, $user_id, $history_id ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # Matcher::matchサブルーチン呼び出しに必要な
    # ひらがな/カタカナの大/小文字区別モード値・Variableインスタンスを取得
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $variable                         = $self->{variable};

    foreach my $restricted_set_str ( @{$restricted_settings_array_ref} ) {

        # 設定文字列のUTF8フラグを変換し、「:」で区切って配列とする
        ($restricted_set_str) = @{ $self->_convert_utf8_flag( $restricted_set_str, UTF8_FLAG_FORCE_ON ) };
        my @restricted_set_array = @{ $self->number_of_elements_fixed_split( $restricted_set_str, 5, UTF8_FLAG_AS_IS_INPUT ) };
        if ( scalar(@restricted_set_array) != 5 ) {

            # 要素数が正しくないため、次のループへ
            next;
        }

        # プライベートブラウジングモードの判定
        if ( $restricted_set_array[3] eq '1' && !$is_private ) {

            # プライベートブラウジングモードではなかったので次のループへ
            next;
        }

        # 判定無視項目の設定
        foreach my $i ( 1, 2 ) {
            if ( $restricted_set_array[$i] eq '-' ) {

                # 「-」のみの場合に「」(空)に置き換える
                $restricted_set_array[$i] = '';
            }
        }

        # ホストとUserAgent・CookieA or 登録ID or 書込IDの両方が空値の場合はスキップ
        if ( $restricted_set_array[1] eq '' && $restricted_set_array[2] eq '' ) {
            next;
        }

        # スレッド名判定
        if (!defined(
                match( [$thread_title], [ $restricted_set_array[0] ], $hiragana_katakana_normalize_mode, undef(), undef(), $variable )
            )
            )
        {

            # 一致しないときは次のループへ
            next;
        }

        # ホストとUserAgentの組み合わせ判定
        if ( $restricted_set_array[1] ne '' ) {
            my ($host_useragent_match_array) = @{
                $self->get_matched_host_useragent_and_whether_its_not_match( $host, $useragent, $restricted_set_array[1],
                    undef(), UTF8_FLAG_FORCE_ON )
            };
            if ( defined($host_useragent_match_array) ) {
                return 1;
            }
        }

        # CookieA or 登録ID or 書込ID判定
        if ( $restricted_set_array[2] ne '' ) {
            my ($cookiea_userid_historyid_match_array) = @{
                $self->get_matched_cookiea_userid_historyid_and_whether_its_not_match( $cookie_a, $user_id, $history_id,
                    $restricted_set_array[2],
                    UTF8_FLAG_FORCE_ON )
            };
            if ( defined($cookiea_userid_historyid_match_array) ) {
                return 1;
            }
        }
    }

    # いずれの設定にも一致しなかった
    return;
}

# 名前欄非表示機能の一致判定を行うサブルーチン
#
# 第1引数: スレッド名
# 第2引数: 名前欄非表示機能 設定配列への配列リファレンス
sub is_hide_name_field_in_form {
    my ( $self, $thread_title, $target_array_ref ) = @_;
    if ( ref($target_array_ref) ne 'ARRAY' ) {
        return;
    }

    # スレッド名のUTF8フラグを変換
    ($thread_title) = @{ $self->_convert_utf8_flag( $thread_title, UTF8_FLAG_FORCE_ON ) };

    # Matcher::matchサブルーチン呼び出しに必要な
    # ひらがな/カタカナの大/小文字区別モード値・Variableインスタンスを取得
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $variable                         = $self->{variable};

    # 設定値要素ループ
    foreach my $target_str ( @{$target_array_ref} ) {

        # 空値の場合はスキップ
        if ( $target_str eq '' ) {
            next;
        }

        # 設定値のUTF8フラグを変換
        ($target_str) = @{ $self->_convert_utf8_flag( $target_str, UTF8_FLAG_FORCE_ON ) };

        # 一致判定
        if ( defined( match( [$thread_title], [$target_str], $hiragana_katakana_normalize_mode, undef(), undef(), $variable ) ) ) {

            # 一致していたので返す
            return 1;
        }
    }

    # 1つも一致しなかった
    return;
}

sub _extract_variable {
    my ( $self, $str ) = @_;

    my $variable = $self->{variable};
    if ( defined($variable) ) {
        return $variable->extract_variable($str);
    } else {
        return $str;
    }
}

sub _convert_result_str_array_utf8_flag {
    my ( $self, $results, $orig_flag, $mode ) = @_;
    if ( $mode != UTF8_FLAG_AS_IS_INPUT && $mode != UTF8_FLAG_FORCE_ON && $mode != UTF8_FLAG_FORCE_OFF ) {
        confess('$mode must set be UTF8_FLAG_AS_IS_INPUT or UTF8_FLAG_FORCE_ON or UTF8_FLAG_FORCE_OFF.');
    }
    if ( !defined($results) || !defined($orig_flag) && $mode == UTF8_FLAG_AS_IS_INPUT ) {
        return $results;
    }

    my $convert_to;
    if ( $mode == UTF8_FLAG_AS_IS_INPUT ) {
        $convert_to = $orig_flag ? UTF8_FLAG_FORCE_ON : UTF8_FLAG_FORCE_OFF;
    } else {
        $convert_to = $mode;
    }
    foreach my $targets_array ( @{$results} ) {
        foreach my $or_array ( @{$targets_array} ) {
            foreach my $element ( @{$or_array} ) {
                ($element) = @{ $self->_convert_utf8_flag( $element, $convert_to ) };
            }
        }
    }

    return $results;
}

sub _convert_utf8_flag {
    my ( $self, $str, $mode ) = @_;
    if ( $mode != UTF8_FLAG_AS_IS_INPUT && $mode != UTF8_FLAG_FORCE_ON && $mode != UTF8_FLAG_FORCE_OFF ) {
        confess('$mode must set be UTF8_FLAG_AS_IS_INPUT or UTF8_FLAG_FORCE_ON or UTF8_FLAG_FORCE_OFF.');
    }
    my $is_utf8 = Encode::is_utf8($str);

    if ( $mode == UTF8_FLAG_AS_IS_INPUT ) {
        return [ $str, $is_utf8 ];
    }

    my Encode::Encoding $enc_cp932 = $self->{enc_cp932};
    if ($is_utf8) {
        if ( $mode == UTF8_FLAG_FORCE_OFF ) {
            $str = $enc_cp932->encode($str);
        }
    } else {
        if ( $mode == UTF8_FLAG_FORCE_ON ) {
            $str = $enc_cp932->decode($str);
        }
    }
    return [ $str, $is_utf8 ];
}

1;
