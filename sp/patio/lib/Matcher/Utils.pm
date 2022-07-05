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

# UTF8�t���O����Ȃ�
# ������̈�v������s���T�u���[�`��
#
# ��1���� : ����Ώە�����̔z�񃊃t�@�����X
# ��2���� : ��v���ҕ�����̔z�񃊃t�@�����X
# ��3���� : ��v�ݒ蕶����̐ړ���������̔z�񃊃t�@�����X (undef�͉����t�����Ȃ�) (['@ ', undef, undef, undef]�Ȃ�)
# ��4���� : �S��v���̐ݒ蕶����u��������̔z�񃊃t�@�����X (undef�͔���Ώۂ̕����񂻂̂܂܂Ƃ���) (['**', undef, undef, undef]�Ȃ�)
# ��5���� : �Ԃ�l��UTF8�t���O
sub universal_match {
    my ( $self, $targets, $expects, $match_prefixes, $all_matches, $result_utf8mode ) = @_;

    # ����Ώۂ���ѐݒ�l��UTF8�t���O��ϊ�
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

    # ������{
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $variable                         = $self->{variable};
    my $results = match( $targets, $expects, $hiragana_katakana_normalize_mode, $match_prefixes, $all_matches, $variable );

    # ���茋��UTF8�t���O�ϊ�
    $results = $self->_convert_result_str_array_utf8_flag( $results, $original_utf8flag, $result_utf8mode );

    return $results;
}

# �^����ꂽ��������u:�v�ŋ�؂��Ĕz�񃊃t�@�����X�ŕԂ��܂�
# ���҂��锻��g�ݍ��킹���ȏ�ɕ����ł���ꍇ�́A�擪�̗v�f�ɗ]��v�f���������܂�
#
# ��1����: ������
# ��2����: ���҂��锻��g�ݍ��킹��
# ��3����: �Ԃ�l��UTF8�t���O
sub number_of_elements_fixed_split {
    my ( $self, $set_str, $expect_elements_count, $result_utf8mode ) = @_;

    # ���͕������UTF8�t���O��ϊ�
    my $orig_utf8flag;
    ( $set_str, $orig_utf8flag ) = @{ $self->_convert_utf8_flag( $set_str, UTF8_FLAG_FORCE_ON ) };

    my @set_array = split( /:/, $set_str, -1 ); # �u:�v�ŋ�؂��Ĕz��Ƃ���
    my $elements_count = scalar(@set_array);    # �����v�f�����擾

    # �v�f�����Ґ������̎��͂���z�񃊃t�@�����X��Ԃ�
    if ( $elements_count < $expect_elements_count ) {
        return [];
    }

    # �v�f�����Ґ��ȏ�̎��́A0�`(�]��v�f��)�܂ł�index�̗v�f�ɂ��āu:�v�Ō�������
    if ( $elements_count > $expect_elements_count ) {
        my $last_concat_index = $elements_count - $expect_elements_count; # ��������Ō�̗v�f��index
        @set_array = ( join( ':', @set_array[ 0 .. ($last_concat_index) ] ), @set_array[ ( $last_concat_index + 1 ) .. $#set_array ] );
    }

    # �Ԃ�l��UTF8�t���O��ϊ�
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

# ���ݎ����A��������Time::Piece�ɂ��w�莞����
# �w�菑��������ł̎��Ԕ͈͂��ǂ����𔻒肷��T�u���[�`��
#
# ��1����: ���Ԕ͈͕�����
# ��2����(�I�v�V����): Time::Piece�C���X�^���X�̔���Ώێ���
sub is_in_time_range {
    my ( $self, $time_range_str, $opt_time_to_check_time_piece_instance ) = @_;

    ($time_range_str) = @{ $self->_convert_utf8_flag( $time_range_str, UTF8_FLAG_FORCE_ON ) };

    local ( $1, $2 );
    if ( $time_range_str =~ /^((?:[0-1][0-9]|2[0-3])[0-5][0-9])-((?:[0-1][0-9]|2[0-3])[0-5][0-9])$/ ) {
        my $now_time_piece_instance = $self->{now_time_piece_instance};

        # ����������ꍇ�͎w������A�Ȃ��ꍇ�͌��ݓ�����Time::Piece�C���X�^���X���g�p����
        my $time_to_check = $opt_time_to_check_time_piece_instance || $now_time_piece_instance;

        # �������Z�b�g����Time::Piece�C���X�^���X���쐬
        my $from = localtime( Time::Piece->strptime( $now_time_piece_instance->ymd . ' ' . $1, '%Y-%m-%d %H%M' ) );
        my $to   = localtime( Time::Piece->strptime( $now_time_piece_instance->ymd . ' ' . $2, '%Y-%m-%d %H%M' ) );
        ## Time::Piece 1.15�ȉ��̃o�O�ȂǂŁA�^�C���]�[�����قȂ�ꍇ�A�I�t�Z�b�g�b�����Z���Ď��Ԃ𑵂���
        if ( $from->tzoffset != $time_to_check->tzoffset ) {
            my $offset = $from->tzoffset - $time_to_check->tzoffset;
            $from += $offset;
            $to   += $offset;
        }
        if ( $from > $to ) {

            # $from����$to�̎������O�ƂȂ��Ă���ꍇ�A���t���܂����������̎w��Ƃ���
            $to += ONE_DAY;
        }

        # $to��59�b�܂łȂ̂ŉ��Z����
        $to += 59;

        # $time_to_check���A$from�ȏ� ���� $to�ȉ�(=�͈͓��̎���)�ł��邩�ǂ�����Ԃ�
        return $from <= $time_to_check && $time_to_check <= $to;
    } else {

        # �������������Ȃ�����undef��Ԃ�
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

    # ����������ꍇ�͎w������A�Ȃ��ꍇ�͌��ݓ�����Time::Piece�C���X�^���X���g�p����
    my $now_time_piece_instance = $self->{now_time_piece_instance};
    my $time_to_check = $opt_time_to_check_time_piece_instance || $now_time_piece_instance;

    # �Ώ۔͈͂̎n�߂ƏI����Time::Piece�C���X�^���X���쐬
    my $from = localtime( Time::Piece->strptime( $start_datetime, '%Y/%m/%d %H:%M' ) );
    my $to = localtime( Time::Piece->strptime( $start_datetime, '%Y/%m/%d %H:%M' ) ) + ( ONE_HOUR * $effective_hour );

    # Time::Piece 1.15�ȉ��̃o�O�ȂǂŁA�^�C���]�[�����قȂ�ꍇ�A�I�t�Z�b�g�b�����Z���Ď��Ԃ𑵂���
    if ( $from->tzoffset != $time_to_check->tzoffset ) {
        my $offset = $from->tzoffset - $time_to_check->tzoffset;
        $from += $offset;
        $to   += $offset;
    }

    # �L�����Ԕ͈͓����ǂ������肵�ĕԂ�
    return $from <= $time_to_check && $to > $time_to_check;
}

# �z�X�g��UserAgent�̑g�ݍ��킹�̎w��ň�v�����g�ݍ��킹��Ԃ��T�u���[�`��
#
# ��1����: �z�X�g
# ��2����: UserAgent (�z�X�g�݂̂�UserAgent�̔�����s��Ȃ��ꍇ��undef)
# ��3����: ��v������s���A�z�X�g��UserAgent�̑g�ݍ��킹�̐ݒ蕶����
# ��4����: �S��v���̕������v�f��2�̔z�񃊃t�@�����X�Ŏw��(undef�͔���Ώۂ̕����񂻂̂܂܂Ƃ���) (�� ['**', undef])
# ��5����: �Ԃ�l��UTF8�t���O
#
# �Ԃ�l: ��v����ł����ꂩ�ɕ�����v�����ꍇ�́A[[(�z�X�g��v���ʔz�񃊃t�@�����X), (UserAgent��v���ʔz�񃊃t�@�����X)], 0]��Ԃ�
#         �s��v����ł�������s��v�̏ꍇ�́A[[(�s��v�t���O�t�z�X�g�ݒ�l�̔z�񃊃t�@�����X), (�s��v�t���O�tUserAgent�ݒ�l�̔z�񃊃t�@�����X)], 1]��Ԃ�
#         ���������v/�����ꂩ�ɕs��v���Ȃ���΁A[undef, ��v����̏ꍇ��0/�s��v����̏ꍇ��1]��Ԃ�
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

    my @match_expect_settings;     # ��v����ݒ�l�̔z��
    my @not_match_expect_settings; # �s��v����ݒ�l�̔z��
    my @not_match_hosts;           # �s��v���ɏo�͂���z�X�g�ݒ�l�̔z��
    my @not_match_useragents;      # �s��v���ɏo�͂���UserAgent�ݒ�l�̔z��

    # $host��IP�A�h���X�Ɋ��S��v�������ǂ���
    my $ip_matched_flag = $host =~ /^(?:(?:2(?:[0-4]\d|5[0-5])|1\d{2}|[1-9]\d|\d)\.){3}(?:2(?:[0-4]\d|5[0-5])|1\d{2}|[1-9]\d|\d)$/;

    # �ݒ蕶�����UTF8�t���O��ϊ�
    my $setting_str_utf8flag;
    ( $setting_str, $setting_str_utf8flag ) = @{ $self->_convert_utf8_flag( $setting_str, UTF8_FLAG_FORCE_ON ) };
    $all_match_strs = [ map { defined($_) ? ${ $self->_convert_utf8_flag( $_, UTF8_FLAG_FORCE_ON ) }[0] : $_ } @{$all_match_strs} ];

    # �ϐ��W�J
    $setting_str = $self->_extract_variable($setting_str);

    foreach my $host_useragent_set_str ( ( grep { $_ ne '' && $_ ne '-' } split( /��/, $setting_str ) ) ) {
        my ( $target_hosts_str, $target_useragents_str ) = split( /<>/, $host_useragent_set_str, 2 );
        if ( !defined($target_hosts_str) || $target_hosts_str eq '' ) {

            # �ݒ�l�̃z�X�g����`����Ă��Ȃ��ꍇ�̓X�L�b�v
            next;
        }

        # �z�X�g��UserAgent�̑g�ݍ��킹���画�荀�ڂ𕪊�
        my @target_hosts = grep { $_ ne '' } ( split( /,/, $target_hosts_str ) );
        my @target_useragents;
        if ( defined($target_useragents_str) ) {
            @target_useragents = grep { $_ ne '' } ( split( /,/, $target_useragents_str ) );
        }

        # ����Ώۂ�UserAgent�̎w�肪�Ȃ��̂ɁA�ݒ�l�Ƃ���UserAgent���w�肳��Ă���Ƃ��̓X�L�b�v
        if ( !defined($useragent) && scalar(@target_useragents) >= 1 ) {
            next;
        }

        # ��v���肩�s��v���肩�𔻕�
        my $is_normal_match = all { substr( $_, 0, 1 ) ne '!' } ( @target_hosts, @target_useragents );
        my @orig_target_hosts_for_not_match;
        if ( !$is_normal_match ) {

            # �ݒ蕶���񂪕s��v����̏ꍇ�A�s��v�t���O�t��������ɍi��A�s��v�t���O����菜��
            @orig_target_hosts_for_not_match = grep { substr( $_, 0, 1 ) eq '!' } @target_hosts;
            @target_hosts = map { substr( $_, 1 ); } @target_hosts;
        }

        # ����ΏۂƔ���ݒ�̃y�A���쐬
        my @target_settings_pairs = ( [ [ ($host) x scalar(@target_hosts) ], \@target_hosts ] );
        if ( ( my $target_useragents_length = scalar(@target_useragents) ) ) {
            push( @target_settings_pairs, [ [ ($useragent) x $target_useragents_length ], \@target_useragents ] );
        }

        # ���ꂼ��̐ݒ�l�z��ɒǉ�
        if ($is_normal_match) {

            # �ݒ蕶���񂪈�v����̏ꍇ
            push( @match_expect_settings, \@target_settings_pairs );
        } else {

            # �ݒ蕶���񂪕s��v����̏ꍇ
            push( @not_match_expect_settings, \@target_settings_pairs );
            push( @not_match_hosts,           @orig_target_hosts_for_not_match );
            push( @not_match_useragents,      @target_useragents );
        }
    }

    # ����g�ݍ��킹�쐬
    my $is_not_match_int_flag = scalar(@not_match_expect_settings) > 0 ? 1 : 0;
    my $judge_combis = $is_not_match_int_flag ? \@not_match_expect_settings : \@match_expect_settings;

    # ������{
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my @setting_result                   = ( [], [] );
    my @target_result                    = ( [], [] );
COMBIS_LOOP:
    foreach my $combi_ref ( @{$judge_combis} ) {
        my @combi        = @{$combi_ref};
        my $combi_length = scalar(@combi);
        my ( @combi_result, @target_combi_result );

        # ����Ώۂ��ƂɈ�v������s��
    PAIR_LOOP: for ( my $i = 0; $i < $combi_length; $i++ ) { # 0: Host, 1: UserAgent
            my ( $targets, $settings ) = @{ $combi[$i] };
            my $current_all_match_strs = [ ( ${$all_match_strs}[$i] ) x scalar( @{$targets} ) ];

            # �z�X�g�̈�v����̏ꍇ�AIP�A�h���X��v������s�����ǂ����𔻒�
            if ( $i == 0 ) {

                # �ݒ�z���$ip���܂ޗv�findex���n�b�V���Ŏ擾
                my %ip_indexes = map { ${$settings}[$_] eq '$ip' ? ( $_ => 1 ) : (); } ( 0 .. $#{$settings} );

                # IP�A�h���X��v����
                if ( scalar( keys(%ip_indexes) ) >= 1 ) {
                    if ($ip_matched_flag) {

                        # ��v���ʂƂ���$ip���Z�b�g
                        push( @combi_result, ['$ip'] );
                        push( @target_combi_result, [$host] );
                        next PAIR_LOOP;
                    } else {

                        # IP�A�h���X��v���Ȃ��������߁A
                        # $ip��������$targets��$settings�Ƀt�B���^�����O���Ĉ�v������p������
                        # ($current_all_match_strs��$targets�̗v�f���ɍ��킹��)
                        $targets  = [ ( map { exists( $ip_indexes{$_} ) ? ${$targets}[$_]  : () } ( 0 .. $#{$targets} ) ) ];
                        $settings = [ ( map { exists( $ip_indexes{$_} ) ? ${$settings}[$_] : () } ( 0 .. $#{$settings} ) ) ];
                        $current_all_match_strs = [ ( ${$all_match_strs}[$i] ) x scalar( @{$targets} ) ];
                    }
                }
            }

            # ��v����
            my $tmp_match_results = match( $targets, $settings, $hiragana_katakana_normalize_mode, undef(), $current_all_match_strs );

            # �s��v�̏ꍇ�͎��̃Z�b�g
            if ( !defined($tmp_match_results) ) {
                next COMBIS_LOOP;
            }

            # �}�b�`�����ݒ�����o��
            push( @combi_result, [ grep { defined($_) } map { ${ ${$_}[0] }[0] } @{$tmp_match_results} ] );

            # �}�b�`�����Ώۂ����o��
            push( @target_combi_result, [ grep { defined($_) && $_ ne '' } map { ${ ${$_}[0] }[1] } @{$tmp_match_results} ] );
        }

        # �S�̂̌��ʔz��ɒǉ�
        for ( my $i = 0; $i < 2; $i++ ) {
            if ( $i < $combi_length ) {
                push( @{ $setting_result[$i] }, @{ $combi_result[$i] } );
                push( @{ $target_result[$i] },  @{ $target_combi_result[$i] } );
            } elsif ( defined( ${$all_match_strs}[$i] ) ) {

                # UserAgent�̈�v������s��Ȃ�����Ώ�/�ݒ�̑g�ݍ��킹�̏ꍇ
                # ��v�ݒ�z��ɂ̂݁A�S��v�������ǉ�����
                push( @{ $setting_result[$i] }, ${$all_match_strs}[$i] );
            }
        }

        if ($is_not_match_int_flag) {
            last COMBIS_LOOP;
        }
    }

    # ���茋�ʍ쐬
    my ( $setting_result_array_ref, $target_result_array_ref );
    if ( !$is_not_match_int_flag ) {

        # ��v����
        if ( scalar( @{ $setting_result[0] } ) > 0 ) {

            # ��v���ʂ�����ꂽ�ꍇ
            $setting_result_array_ref = \@setting_result;
            $target_result_array_ref  = \@target_result;
        }
    } else {

        # �s��v����
        if ( scalar( @{ $setting_result[0] } ) == 0 ) {

            # �S�Ăɕs��v�������ꍇ
            $setting_result_array_ref = [ \@not_match_hosts, \@not_match_useragents ]; # �s��v�t���O������擪�ɕt�����ݒ�l�̔z���Ԃ�
            $target_result_array_ref = [ [], [] ];                                     # ��v���锻��Ώۂ͂Ȃ��̂ŁA���������z���Ԃ�
        }
    }

    # ���茋��UTF8�t���O�ϊ�
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

# CookieA or �o�^ID or ����ID�̊��S��v������s���T�u���[�`��
#
# ��1����: CookieA
# ��2����: �o�^ID
# ��3����: ����ID
# ��4����: ��v������s���ACookieA or �o�^ID or ����ID�̐ݒ蕶����
# ��5����: �Ԃ�l��UTF8�t���O
#
# �Ԃ�l: ��v����̏ꍇ�A�����ꂩ�Ɋ��S��v������[[(CookieA��v���ʔz�񃊃t�@�����X), (�o�^ID��v���ʔz�񃊃t�@�����X), (����ID��v���ʔz�񃊃t�@�����X)], 0]��Ԃ�
#         �s��v����̏ꍇ�A�S�Ăɕs��v�������ꍇ[[[],[],[]], 1]��Ԃ�
#         ���������v/�����ꂩ�ɕs��v���s��v���Ȃ������ꍇ�A[undef, ��v����̏ꍇ��0/�s��v����̏ꍇ��1]��Ԃ�
sub get_matched_cookiea_userid_historyid_and_whether_its_not_match {
    my ( $self, $cookie_a, $user_id, $history_id, $setting_str, $result_utf8mode ) = @_;

    # ����Ώۂ���ѐݒ�l��UTF8�t���O��ϊ�
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

    # ���茋��UTF8�t���O�m��
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

    # �ݒ蕶����𕪊����A�ے�w��̐ݒ肪����ꍇ�͂��̐ݒ�݂̂ɍi��
    my @judge_items = grep { $_ ne '' && $_ ne '-' } split( /,/, $setting_str );
    my @not_judge_items = map { substr( $_, 0, 1 ) eq '!' ? substr( $_, 1 ) : () } @judge_items;
    my $is_normal_match = scalar(@not_judge_items) == 0;
    if ( !$is_normal_match ) {
        @judge_items = @not_judge_items;
    }

    # ��v/�s��v����Ώۍ��ڒ�`
    my @targets = ( $cookie_a, $user_id, $history_id );

    # ��v/�s��v���� (OR����)
    my @result_array;
    foreach my $target (@targets) {
        if ( defined($target) && $target ne '' ) {
            push( @result_array, [ ( map { ${ $self->_convert_utf8_flag( $_, $convert_to ) }[0] } grep { $_ eq $target } @judge_items ) ] );
        } else {
            push( @result_array, [] );
        }
    }

    # ���茋�ʍ쐬
    if ( any { scalar( @{$_} ) >= 1 } @result_array ) {

        # ���S��v���鍀�ڂ�1�ȏ゠�����ꍇ
        # (�S�ĂɊ��S��v or �S�Ăł͂Ȃ����s��v�̍��ڂ�����ꍇ���܂�)
        if ($is_normal_match) {

            # ��v����
            return [ \@result_array, 0 ];
        } else {

            # �s��v����
            return [ undef(), 1 ];
        }
    } else {

        # ���S��v���鍀�ڂ�1���Ȃ������ꍇ
        # (�S�Ăɕs��v�������ꍇ)
        if ($is_normal_match) {

            # ��v����
            return [ undef(), 0 ];
        } else {

            # �s��v����
            return [ \@result_array, 1 ]; # @result_array == [ ( [] ) x scalar(@targets) ] �ƂȂ��Ă���
        }
    }
}

# �X���b�h����v����ݒ�l�Ƃ̈�v������s���T�u���[�`��
#
# ��1����: ����ΏۃX���b�h�� (�����G���R�[�h�ϊ���̒l�ł��ǂ�)
# ��2����: �X���b�h����v����ݒ�l
# ��3����: �ʏ��v�݂̂̔���Ƃ��邩�ǂ��� (undef�́A�ݒ�l�ɔے�w�肪����ꍇ�A�ے��v�݂̂̔�����s��)
# ��4����: ��v���ɐ擪�ɕt�����镶������w��(undef�͉����t�����Ȃ�)
# ��5����: �S��v���̕�������w��(undef�͔���Ώۂ̕����񂻂̂܂܂Ƃ���)
# ��6����: �Ԃ�l��UTF8�t���O
#
# �Ԃ�l: ��v����̏ꍇ�A�����ꂩ�Ɉ�v������[(��v���ʔz�񃊃t�@�����X), 0]��Ԃ�
#         �s��v����̏ꍇ�A�S�Ăɕs��v�������ꍇ[[], 1]��Ԃ�
#         �S�Ĉ�v���Ȃ�/�S�Ăɕs��v�ł͂Ȃ������ꍇ�A[undef, ��v����̏ꍇ��0/�s��v����̏ꍇ��1]��Ԃ�
sub get_matched_thread_title_to_setting_and_whether_its_not_match {

    # �����`�F�b�N�E�W�J
    my ( $self, $thread_title, $setting_str, $normal_match_only_flg, $match_prefix_str, $wildcard_match_str, $result_utf8mode ) = @_;
    if ( $thread_title eq '' || $setting_str eq '' ) {
        return [ undef(), 0 ];
    }

    # �K�v�ɉ����ăX���b�h��������G���R�[�h�ɕϊ�
    my $thread_title_utf8flag;
    ( $thread_title, $thread_title_utf8flag ) = @{ $self->_convert_utf8_flag( $thread_title, UTF8_FLAG_FORCE_ON ) };

    # �ݒ蕶�����K�v�ɉ����ē����G���R�[�h�ɕϊ�
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

    # �ϐ��W�J
    my $variable_extracted_setting_str = $self->_extract_variable($setting_str);

    # �ݒ蕶����𕪊����A�����D��t���O�ɉ����Ĕے�w��̐ݒ肪����ꍇ�͂��̐ݒ�݂̂ɍi��
    my @judge_items = grep { $_ ne '' } @{ Matcher::_expect_split( $variable_extracted_setting_str, 0, ',' ) };
    my $is_normal_match = 1;
    if ($normal_match_only_flg) {

        # �ʏ��v�����̂�
        @judge_items = grep { substr( $_, 0, 1 ) ne '!' } @judge_items;
    } else {

        # �ے��v�����D��
        my @not_judge_items = map { substr( $_, 0, 1 ) eq '!' ? substr( $_, 1 ) : () } @judge_items;
        $is_normal_match = scalar(@not_judge_items) == 0;
        if ( !$is_normal_match ) {
            @judge_items = @not_judge_items;
        }
    }

    # OR�������Č������āA�ʏ�̈�v������s��
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $rejoined_setting_str = join( ',', @judge_items );
    my $matched_title_array_ref
        = match( [$thread_title], [$rejoined_setting_str], $hiragana_katakana_normalize_mode, [$match_prefix_str], [$wildcard_match_str] );

    # ���茋�ʂ��쐬
    if ( defined($matched_title_array_ref) ) {

        # �ꕔ�܂��͑S������v���Ă����ꍇ
        if ($is_normal_match) {

            # ��v����

            # ��v���ʂ�UTF8�t���O��ϊ�
            $self->_convert_result_str_array_utf8_flag( $matched_title_array_ref, $thread_title_utf8flag, $result_utf8mode );

            # ���ʔz��̎������팸���ĕԂ� (��v���ڂ͂��Ƃ��1�Ȃ̂�)
            return [ ${$matched_title_array_ref}[0], 0 ];
        } else {

            # �s��v����
            return [ undef(), 1 ];
        }
    } else {

        # �S�Ăɕs��v�������ꍇ
        if ($is_normal_match) {

            # ��v����
            return [ undef(), 0 ];
        } else {

            # �s��v����
            return [ [], 1 ];
        }
    }
}

# ���O����v����ݒ�l�Ƃ̈�v������s���T�u���[�`��
# ��1���� : ����v�f�ʂ̔���Ώە�����
# ��2���� : ���O��v����g�ݍ��킹�ݒ�l�̔z�񃊃t�@�����X
# ��3���� : �Ԃ�l��UTF8�t���O
sub get_matched_name_to_setting {

    # �����`�F�b�N�E�W�J
    my ( $self, $raw_name, $setting_str, $result_utf8mode ) = @_;
    if ( $raw_name eq '' || $setting_str eq '' ) {
        return;
    }

    if ( $setting_str eq '*' ) {
        return ['*'];
    }

    # ���O������G���R�[�h�ɕϊ�
    my ( $utf8flagged_raw_name, $raw_name_utf8flag ) = @{ $self->_convert_utf8_flag( $raw_name, UTF8_FLAG_FORCE_ON ) };
    my ($utf8notflagged_raw_name) = @{ $self->_convert_utf8_flag( $raw_name, UTF8_FLAG_FORCE_OFF ) };

    # �ݒ蕶���������G���R�[�h�ɕϊ�
    my $setting_str_utf8flag;
    ( $setting_str, $setting_str_utf8flag ) = @{ $self->_convert_utf8_flag( $setting_str, UTF8_FLAG_FORCE_ON ) };

    if ( $raw_name_utf8flag != $setting_str_utf8flag && $result_utf8mode == UTF8_FLAG_AS_IS_INPUT ) {
        confess('Cannot use UTF8_FLAG_AS_IS_INPUT as $result_utf8mode. ($raw_name_utf8flag != $setting_str_utf8flag)');
    }

    # �g���b�v�ϊ��T�u���[�`�����擾
    my $trip_subroutine = $self->{trip_subroutine};

    # �g���b�v�ϊ���̖��O�𐶐����A�����G���R�[�h�ɕϊ�
    my ($trip_converted_name) = @{ $self->_convert_utf8_flag( $trip_subroutine->($utf8notflagged_raw_name), UTF8_FLAG_FORCE_ON ) };

    # ������s�����O���� �����T�u���[�`��
    my $get_match_target_name_from_setting_str = sub {
        my ($set_str) = @_;
        my @ret_targets;

        # �ݒ蕶����Ƀg���b�v�V�[�h/�g���b�v���ʎq���܂ނ��ǂ���
        my $trip_seed_flag = index( $set_str, '#' ) != -1;
        my $trip_flag      = index( $set_str, '��' ) != -1;

        # �ݒ�l�Ƀg���b�v�V�[�h���܂ގw�肪���邽�߁A
        # ���O����ł��܂߂Ĕ�����s��
        if ($trip_seed_flag) {

            # �g���b�v�ϊ��O�̖��O���g�p (�g���b�v�V�[�h�����܂�)
            push( @ret_targets, $utf8flagged_raw_name );
        }

        # �ݒ�l�Ƀg���b�v���܂ގw�肪���邽�߁A
        # ���O����ł��܂߂Ĕ�����s��
        if ($trip_flag) {

            # �g���b�v�ϊ���̖��O���g�p (�g���b�v�����܂�)
            push( @ret_targets, $trip_converted_name );
        }

        # �ǂ���̎w����Ȃ��ꍇ
        if ( !$trip_flag && !$trip_seed_flag ) {

            # �ʏ�̖��O�����݂̂̔���
            # �g���b�v�ϊ��O�̖��O���g�p (�g���b�v�V�[�h/�g���b�v�����܂܂�)
            push( @ret_targets, ( split( /#|��/, $utf8flagged_raw_name, 2 ) )[0] );
        }

        return \@ret_targets;
    };

    # �ϐ��W�J
    my $variable_extracted_setting_str = $self->_extract_variable($setting_str);

    # �ݒ蕶�����OR�����ʂɕ���
    my @or_settings = grep { $_ ne '' } @{ Matcher::_expect_split( $variable_extracted_setting_str, 0, ',' ) };

    # ����ΏہE�ݒ�̑g�ݍ��킹���쐬
    my ( @targets, @expects );
    foreach my $or_setting (@or_settings) {
        my @current_targets = @{ $get_match_target_name_from_setting_str->($or_setting) };
        push( @targets, @current_targets );
        push( @expects, ( ($or_setting) x scalar(@current_targets) ) );
    }

    # ������{
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $match_results = match( \@targets, \@expects, $hiragana_katakana_normalize_mode, undef(), undef(), $self->{variable} );
    if ( !defined($match_results) ) {
        return;
    }

    # ��v���ʂ�UTF8�t���O��ϊ�
    $match_results = $self->_convert_result_str_array_utf8_flag( $match_results, $raw_name_utf8flag, $result_utf8mode );

    # ��v���ʂ̂����A��v�ݒ�݂̂����o���A���j�[�N�����ĕԂ�
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

# �X���b�h��ʂ��烆�[�U�[�𐧌�����@�\�̈�v������s���T�u���[�`��
#
# ��1����: CookieA
# ��2����: �o�^ID
# ��3����: ����ID
# ��4����: �z�X�g
sub is_restricted_user_from_thread_page {
    my ( $self, $cookie_a, $user_id, $history_id, $host ) = @_;

    # ����Ώۂ�UTF8�t���O��ϊ�
    foreach my $target ( $cookie_a, $user_id, $history_id, $host ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # �ݒ�Ȃǎ擾
    my $time                                              = $self->{time};
    my $restrict_user_from_thread_page_target_log_path    = $self->{restrict_user_from_thread_page_target_log_path};
    my $restrict_user_from_thread_page_target_hold_hour_1 = $self->{restrict_user_from_thread_page_target_hold_hour_1};
    my $restrict_user_from_thread_page_target_hold_hour_2 = $self->{restrict_user_from_thread_page_target_hold_hour_2};
    my $restrict_user_from_thread_page_target_hold_hour_3 = $self->{restrict_user_from_thread_page_target_hold_hour_3};
    my $restrict_user_from_thread_page_target_hold_hour_4 = $self->{restrict_user_from_thread_page_target_hold_hour_4};
    my $restrict_user_from_thread_page_target_hold_hour_5 = $self->{restrict_user_from_thread_page_target_hold_hour_5};
    my $restrict_user_from_thread_page_target_hold_hour_6 = $self->{restrict_user_from_thread_page_target_hold_hour_6};
    my $restrict_user_from_thread_page_target_hold_hour_7 = $self->{restrict_user_from_thread_page_target_hold_hour_7};

    # ���O�t�@�C���T�C�Y������e���Ȃ��Ɣ��f�����ꍇ�ɂ́A�ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�
    if ( -s $restrict_user_from_thread_page_target_log_path <= 2 ) {
        return;
    }

    # ���O�p�[�X����
    my @restrict_user_settings_array;
    {
        # ���O�t�@�C���I�[�v�� (���s���́A�ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�)
        open( my $json_log_fh, '<:utf8', $restrict_user_from_thread_page_target_log_path ) || return;
        flock( $json_log_fh, 1 ) || return;

        # ���O�t�@�C���ǂݍ���
        seek( $json_log_fh, 0, 0 );
        local $/;
        my $json_log_contents = <$json_log_fh>;
        close($json_log_fh);

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
            if ( ref($json_parsed_ref) ne 'ARRAY' ) {

                # JSON�̃��[�g���z��łȂ��A�z��ƈقȂ�\���̏ꍇ�A
                # �ݒ�Ɉ�v���Ȃ��������̂Ƃ��ăG���[��Ԃ�
                die();
            }
            @restrict_user_settings_array = @{$json_parsed_ref};
        };
        if ($@) {

            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # �ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�
            return;
        }
    }

    # �p�[�X�����z��̐����ݒ�n�b�V���̂����A�����Ȑ����ݒ����菜��
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

    # ��v����
    foreach my $setting_ref (@restrict_user_settings_array) {

        # �z�X�g����
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

        # CookieA or �o�^ID or ����ID����
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

    # ���ׂĈ�v���Ȃ�����
    return;
}

# �X���b�h��ʂ��烆�[�U�����Ԑ�������@�\�̈�v������s���T�u���[�`��
#
# ��1����: CookieA
# ��2����: �o�^ID
# ��3����: ����ID
# ��4����: �z�X�g
sub is_restricted_user_from_thread_page_by_time_range {
    my ( $self, $cookie_a, $user_id, $history_id, $host ) = @_;

    # ����Ώۂ�UTF8�t���O��ϊ�
    foreach my $target ( $cookie_a, $user_id, $history_id, $host ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # �ݒ�Ȃǎ擾
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

    # �������ԓ��ł��邩�ǂ�������
    if (   !defined($restrict_user_from_thread_page_by_time_range_enable_time_range)
        || !$self->is_in_time_range($restrict_user_from_thread_page_by_time_range_enable_time_range) )
    {
        # �w�肪�Ȃ��ꍇ�A�������́A���ԊO�̏ꍇ�͐ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�
        return;
    }

    # ���O�t�@�C���T�C�Y������e���Ȃ��Ɣ��f�����ꍇ�ɂ́A�ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�
    if ( -s $restrict_user_from_thread_page_by_time_range_target_log_path <= 2 ) {
        return;
    }

    # ���O�p�[�X����
    my @restrict_user_settings_array;
    {
        # ���O�t�@�C���I�[�v�� (���s���́A�ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�)
        open( my $json_log_fh, '<:utf8', $restrict_user_from_thread_page_by_time_range_target_log_path ) || return;
        flock( $json_log_fh, 1 ) || return;

        # ���O�t�@�C���ǂݍ���
        seek( $json_log_fh, 0, 0 );
        local $/;
        my $json_log_contents = <$json_log_fh>;
        close($json_log_fh);

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
            if ( ref($json_parsed_ref) ne 'ARRAY' ) {

                # JSON�̃��[�g���z��łȂ��A�z��ƈقȂ�\���̏ꍇ�A
                # �ݒ�Ɉ�v���Ȃ��������̂Ƃ��ăG���[��Ԃ�
                die();
            }
            @restrict_user_settings_array = @{$json_parsed_ref};
        };
        if ($@) {

            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # �ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�
            return;
        }
    }

    # �p�[�X�����z��̐����ݒ�n�b�V���̂����A�����Ȑ����ݒ����菜��
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

    # ��v����
    foreach my $setting_ref (@restrict_user_settings_array) {

        # �z�X�g����
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

        # CookieA or �o�^ID or ����ID����
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

    # ���ׂĈ�v���Ȃ�����
    return;
}

# �X���b�h��ʂ��烆�[�U�[�𐧌�����@�\ (���̃X���̂�)�̈�v������s���T�u���[�`��
#
# ��1����: �X���b�hNo
# ��2����: CookieA
# ��3����: �o�^ID
# ��4����: ����ID
# ��5����: �z�X�g
sub is_in_thread_only_restricted_user_from_thread_page {
    my ( $self, $thread_number, $cookie_a, $user_id, $history_id, $host ) = @_;

    # ����Ώۂ�UTF8�t���O��ϊ�
    foreach my $target ( $cookie_a, $user_id, $history_id, $host ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # �ݒ�Ȃǎ擾
    my $time = $self->{time};
    my $in_thread_only_restrict_user_from_thread_page_target_log_path
        = $self->{in_thread_only_restrict_user_from_thread_page_target_log_path};
    my $in_thread_only_restrict_user_from_thread_page_target_hold_hour
        = $self->{in_thread_only_restrict_user_from_thread_page_target_hold_hour};

    # ���O�t�@�C���T�C�Y������e���Ȃ��Ɣ��f�����ꍇ�ɂ́A�ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�
    if ( -s $in_thread_only_restrict_user_from_thread_page_target_log_path <= 2 ) {
        return;
    }

    # ���O�p�[�X����
    my %restrict_user_settings_thread_hash;
    {
        # ���O�t�@�C���I�[�v�� (���s���́A�ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�)
        open( my $json_log_fh, '<:utf8', $in_thread_only_restrict_user_from_thread_page_target_log_path ) || return;
        flock( $json_log_fh, 1 ) || return;

        # ���O�t�@�C���ǂݍ���
        seek( $json_log_fh, 0, 0 );
        local $/;
        my $json_log_contents = <$json_log_fh>;
        close($json_log_fh);

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
            if ( ref($json_parsed_ref) ne 'HASH' ) {

                # JSON�̃��[�g���A�z�z��łȂ��A�z��ƈقȂ�\���̏ꍇ�A
                # �ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�
                die();
            }
            %restrict_user_settings_thread_hash = %{$json_parsed_ref};
        };
        if ($@) {

            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # �ݒ�Ɉ�v���Ȃ��������̂Ƃ��ĕԂ�
            return;
        }
    }

    # �\������X���b�hNo�̃L�[���܂܂�Ă��Ȃ��A
    # �������́A�l���z��ł͂Ȃ��ꍇ�́A�ݒ�Ɉ�v���Ă��Ȃ��̂ŕԂ�
    if (  !exists( $restrict_user_settings_thread_hash{$thread_number} )
        || ref( $restrict_user_settings_thread_hash{$thread_number} ) ne 'ARRAY' )
    {
        return;
    }

    # ���̃X���b�h��ΏۂƂ��������ݒ�z����擾���A�����Ȑ����ݒ����菜��
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

    # ��v����
    foreach my $setting_ref (@restrict_user_settings_array) {

        # �z�X�g����
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

        # CookieA or �o�^ID or ����ID����
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

    # ���ׂĈ�v���Ȃ�����
    return;
}

# �z�X�g�Ȃǂɂ��摜�A�b�v���[�h�̖����̈�v������s���T�u���[�`��
#
# ��1����: �X���b�h�� (�V�K�X���b�h�쐬����undef���w��)
# ��2����: �z�X�g
# ��3����: UserAgent(_��-�ɒu�������A,:������)
# ��4����: CookieA
# ��5����: �o�^ID
# ��6����: ����ID
# ��7����: �v���C�x�[�g�u���E�W���O���[�h�ł��邩�ǂ���
# ��8����: �z�X�g�Ȃǂɂ��摜�A�b�v���[�h�̖��� �ݒ�z��ւ̔z�񃊃t�@�����X
sub is_disable_upload_img {
    my ( $self, $thread_title, $host, $useragent, $cookie_a, $user_id, $history_id, $is_private, $restricted_settings_array_ref ) = @_;
    if ( ref($restricted_settings_array_ref) ne 'ARRAY' ) {
        return;
    }

    # ����Ώۂ�UTF8�t���O��ϊ�
    foreach my $target ( $thread_title, $host, $useragent, $cookie_a, $user_id, $history_id ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # Matcher::match�T�u���[�`���Ăяo���ɕK�v��
    # �Ђ炪��/�J�^�J�i�̑�/��������ʃ��[�h�l�EVariable�C���X�^���X���擾
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $variable                         = $self->{variable};

    foreach my $restricted_set_str ( @{$restricted_settings_array_ref} ) {

        # �ݒ蕶�����UTF8�t���O��ϊ����A�u:�v�ŋ�؂��Ĕz��Ƃ���
        ($restricted_set_str) = @{ $self->_convert_utf8_flag( $restricted_set_str, UTF8_FLAG_FORCE_ON ) };
        my @restricted_set_array = @{ $self->number_of_elements_fixed_split( $restricted_set_str, 5, UTF8_FLAG_AS_IS_INPUT ) };
        if ( scalar(@restricted_set_array) != 5 ) {

            # �v�f�����������Ȃ����߁A���̃��[�v��
            next;
        }

        # �v���C�x�[�g�u���E�W���O���[�h�̔���
        if ( $restricted_set_array[3] eq '1' && !$is_private ) {

            # �v���C�x�[�g�u���E�W���O���[�h�ł͂Ȃ������̂Ŏ��̃��[�v��
            next;
        }

        # ���薳�����ڂ̐ݒ�
        foreach my $i ( 1, 2 ) {
            if ( $restricted_set_array[$i] eq '-' ) {

                # �u-�v�݂̂̏ꍇ�Ɂu�v(��)�ɒu��������
                $restricted_set_array[$i] = '';
            }
        }

        # �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�̗�������l�̏ꍇ�̓X�L�b�v
        if ( $restricted_set_array[1] eq '' && $restricted_set_array[2] eq '' ) {
            next;
        }

        # �X���b�h������
        if ( defined($thread_title) ) {

            # ���X���e��
            if (!defined(
                    match( [$thread_title], [ $restricted_set_array[0] ], $hiragana_katakana_normalize_mode, undef(), undef(), $variable )
                )
                )
            {

                # ��v���Ȃ��Ƃ��͎��̃��[�v��
                next;
            }
        } else {

            # �V�K�X���b�h�쐬��
            if ( $restricted_set_array[0] ne '*' ) {

                # �u*�v�̎w�肪�Ȃ��Ƃ��͎��̃��[�v��
                next;
            }
        }

        # �z�X�g��UserAgent�̑g�ݍ��킹����
        if ( $restricted_set_array[1] ne '' ) {
            my ($host_useragent_match_array) = @{
                $self->get_matched_host_useragent_and_whether_its_not_match( $host, $useragent, $restricted_set_array[1],
                    undef(), UTF8_FLAG_FORCE_ON )
            };
            if ( defined($host_useragent_match_array) ) {
                return 1;
            }
        }

        # CookieA or �o�^ID or ����ID����
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

    # ������̐ݒ�ɂ���v���Ȃ�����
    return;
}

# �z�X�g�Ȃǂɂ��age�̖����̈�v������s���T�u���[�`��
#
# ��1����: �X���b�h��
# ��2����: �z�X�g
# ��3����: UserAgent(_��-�ɒu�������A,:������)
# ��4����: CookieA
# ��5����: �o�^ID
# ��6����: ����ID
# ��7����: �v���C�x�[�g�u���E�W���O���[�h�ł��邩�ǂ���
# ��8����: �z�X�g�Ȃǂɂ��age�̖��� �ݒ�z��ւ̔z�񃊃t�@�����X
sub is_disable_age {
    my ( $self, $thread_title, $host, $useragent, $cookie_a, $user_id, $history_id, $is_private, $restricted_settings_array_ref ) = @_;
    if ( ref($restricted_settings_array_ref) ne 'ARRAY' ) {
        return;
    }

    # ����Ώۂ�UTF8�t���O��ϊ�
    foreach my $target ( $thread_title, $host, $useragent, $cookie_a, $user_id, $history_id ) {
        if ( defined($target) ) {
            ($target) = @{ $self->_convert_utf8_flag( $target, UTF8_FLAG_FORCE_ON ) };
        }
    }

    # Matcher::match�T�u���[�`���Ăяo���ɕK�v��
    # �Ђ炪��/�J�^�J�i�̑�/��������ʃ��[�h�l�EVariable�C���X�^���X���擾
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $variable                         = $self->{variable};

    foreach my $restricted_set_str ( @{$restricted_settings_array_ref} ) {

        # �ݒ蕶�����UTF8�t���O��ϊ����A�u:�v�ŋ�؂��Ĕz��Ƃ���
        ($restricted_set_str) = @{ $self->_convert_utf8_flag( $restricted_set_str, UTF8_FLAG_FORCE_ON ) };
        my @restricted_set_array = @{ $self->number_of_elements_fixed_split( $restricted_set_str, 5, UTF8_FLAG_AS_IS_INPUT ) };
        if ( scalar(@restricted_set_array) != 5 ) {

            # �v�f�����������Ȃ����߁A���̃��[�v��
            next;
        }

        # �v���C�x�[�g�u���E�W���O���[�h�̔���
        if ( $restricted_set_array[3] eq '1' && !$is_private ) {

            # �v���C�x�[�g�u���E�W���O���[�h�ł͂Ȃ������̂Ŏ��̃��[�v��
            next;
        }

        # ���薳�����ڂ̐ݒ�
        foreach my $i ( 1, 2 ) {
            if ( $restricted_set_array[$i] eq '-' ) {

                # �u-�v�݂̂̏ꍇ�Ɂu�v(��)�ɒu��������
                $restricted_set_array[$i] = '';
            }
        }

        # �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�̗�������l�̏ꍇ�̓X�L�b�v
        if ( $restricted_set_array[1] eq '' && $restricted_set_array[2] eq '' ) {
            next;
        }

        # �X���b�h������
        if (!defined(
                match( [$thread_title], [ $restricted_set_array[0] ], $hiragana_katakana_normalize_mode, undef(), undef(), $variable )
            )
            )
        {

            # ��v���Ȃ��Ƃ��͎��̃��[�v��
            next;
        }

        # �z�X�g��UserAgent�̑g�ݍ��킹����
        if ( $restricted_set_array[1] ne '' ) {
            my ($host_useragent_match_array) = @{
                $self->get_matched_host_useragent_and_whether_its_not_match( $host, $useragent, $restricted_set_array[1],
                    undef(), UTF8_FLAG_FORCE_ON )
            };
            if ( defined($host_useragent_match_array) ) {
                return 1;
            }
        }

        # CookieA or �o�^ID or ����ID����
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

    # ������̐ݒ�ɂ���v���Ȃ�����
    return;
}

# ���O����\���@�\�̈�v������s���T�u���[�`��
#
# ��1����: �X���b�h��
# ��2����: ���O����\���@�\ �ݒ�z��ւ̔z�񃊃t�@�����X
sub is_hide_name_field_in_form {
    my ( $self, $thread_title, $target_array_ref ) = @_;
    if ( ref($target_array_ref) ne 'ARRAY' ) {
        return;
    }

    # �X���b�h����UTF8�t���O��ϊ�
    ($thread_title) = @{ $self->_convert_utf8_flag( $thread_title, UTF8_FLAG_FORCE_ON ) };

    # Matcher::match�T�u���[�`���Ăяo���ɕK�v��
    # �Ђ炪��/�J�^�J�i�̑�/��������ʃ��[�h�l�EVariable�C���X�^���X���擾
    my $hiragana_katakana_normalize_mode = $self->{hiragana_katakana_normalize_mode};
    my $variable                         = $self->{variable};

    # �ݒ�l�v�f���[�v
    foreach my $target_str ( @{$target_array_ref} ) {

        # ��l�̏ꍇ�̓X�L�b�v
        if ( $target_str eq '' ) {
            next;
        }

        # �ݒ�l��UTF8�t���O��ϊ�
        ($target_str) = @{ $self->_convert_utf8_flag( $target_str, UTF8_FLAG_FORCE_ON ) };

        # ��v����
        if ( defined( match( [$thread_title], [$target_str], $hiragana_katakana_normalize_mode, undef(), undef(), $variable ) ) ) {

            # ��v���Ă����̂ŕԂ�
            return 1;
        }
    }

    # 1����v���Ȃ�����
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
