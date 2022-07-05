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

# ��ʒ萔��`
use constant {
    THREAD_CREATE => 1,
    RESPONSE      => 1 << 1
};

my $disable_setting_char = $enc_cp932->decode('��');
my $restrict_time_char = $enc_cp932->decode('��');
my $additional_hosts_char = $enc_cp932->decode('��');
my $format_capture_regex = qr/^(\d{2}(?:0\d|1[0-2])(?:[0-2]\d|3[0-1])_(?:[01]\d|2[0-3])[0-5]\d)(?:$restrict_time_char(\d+)(?:$additional_hosts_char(.*))?)?$/;

# �����`�F�b�N�T�u���[�`����`
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

# ����Cookie���s���t�t�H�[�}�b�g�T�u���[�`����`
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
        # Time::Piece 1.15�ȉ��̃o�O�ȂǂŃ^�C���]�[�����قȂ�ꍇ�A�I�t�Z�b�g�b�����Z���ĕ\�L��̎��Ԃ𑵂���
        my $offset = $now_time->tzoffset - $first_access_time->tzoffset;
        my $shifted_first_access_time = $first_access_time + $offset;
        return substr($shifted_first_access_time->strftime('%Y%m%d_%H%M'), 2);
    }
}

# ����Cookie���s�T�u���[�`����`
sub issue_cookie {
    my $self = shift;
    if ((caller)[0] ne (caller(0))[0] || !defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance subroutine.');
    }

    # Cookie���s�l�쐬
    my $issue_value = value($self);

    # Cookie���s
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

    # ���ݎ�����Time::Piece �C���X�^���X���擾
    my $NOW_TIME_PIECE_INSTANCE = do {
        local $ENV{TZ} = "JST-9";
        my $tp = localtime($time);
        localtime($time - $tp->sec);
    };

    # CookieA�̒l���擾
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

    # Matcher::Utils�C���X�^���X�擾
    my Matcher::Utils $mu = $matcher_utils_instance;

    # Cookie���s�t���O
    my $issue_cookie_flag = 1;

    # Cookie�ǂݎ��
    foreach my $cookie_set (split(/; */, $ENV{HTTP_COOKIE})) {
        my ($key, $value) = split(/=/, $cookie_set);
        if ($key eq $self{NAME}) {
            if ($value ne '') {
                my $urldecoded_value = $value;
                $urldecoded_value =~ s/\+/ /g;
                $urldecoded_value =~ s/%([0-9a-fA-F]{2})/pack('H2', $1)/eg;
                $urldecoded_value = $enc_utf8->decode($urldecoded_value);
                if ($urldecoded_value =~ $format_capture_regex) {
                    # ����Cookie���s�ςœ��e�̍X�V���s��Ȃ��̂ŁA
                    # ���s�t���O���I�t
                    $issue_cookie_flag = 0;

                    # �����擾
                    # (���񏑂����ݓ����͏���CookieCookie�ɃZ�b�g����Ă���l���g�p)
                    $self{TIME} = localtime(Time::Piece->strptime("20$1", '%Y%m%d_%H%M')); # %Y�̐擪2���������Ă��邽�߁A20??�N�Ƃ��Ĉ���
                    ## Time::Piece 1.15�ȉ��̃o�O�ȂǂŃ^�C���]�[�����قȂ�ꍇ�A�I�t�Z�b�g�b�����Z���Ď��Ԃ𑵂���
                    if ($self{TIME}->tzoffset != $self{NOW}->tzoffset) {
                        my $offset = $self{TIME}->tzoffset - $self{NOW}->tzoffset;
                        $self{TIME} += $offset;
                    }

                    # ����Cookie�ɐ������Ԃ�ێ����Ă���ꍇ�͎擾
                    if (defined($2)) {
                        $self{RESTRICT_HOUR} = int($2);
                    }

                    # ����Cookie�ɒǉ�����z�X�g��ێ����Ă���ꍇ�͎擾
                    if (defined($3)) {
                        $self{ADD_JUDGE_HOSTS} = [uniq(grep { $_ ne '' } split(/,/, $3))];
                    }
                }
            }
            last;
        }
    }

    # �O���t�@�C���I�[�v��
    open(my $setting_fh, '<', $setting_filepath) || croak("Open error: $setting_filepath");
    flock($setting_fh, 1) || croak("Lock error: $setting_filepath");
    $self{SETTING_FH} = $setting_fh;

    # �w�b�_�s�ǂݔ�΂�
    <$setting_fh>;

    # �O���t�@�C�����p�[�X���A�L���Ȑݒ��ǂݍ���
    my @thread_create_valid_settings;
    my @response_valid_settings;
    my @judge_hosts = ($host, @{$self{ADD_JUDGE_HOSTS}});
    while (my $line = <$setting_fh>) {
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @settings = split(/\^/, $line, - 1);
        if (scalar(@settings) != 8 || $settings[0] eq $disable_setting_char) {
            # 8��ł͂Ȃ����O�s�A�������́A������Ɂ��̗�̓X�L�b�v
            next;
        }

        # �ݒ��ʂ��擾
        my $type = int($settings[2]);
        if (!($type & (THREAD_CREATE | RESPONSE))) {
            # �X���쐬or���X��̎w�肪�������Ȃ��ݒ�s�̓X�L�b�v
            next;
        }

        # ���ԗ�̃`�F�b�N
        $settings[5] = int($settings[5]);
        if ($settings[5] <= 0) {
            # �w�肪�������Ȃ��ꍇ�̓X�L�b�v
            next;
        }

        # �v���C�x�[�g���[�h�ɂ��A�N�Z�X�ł͂Ȃ��ꍇ�ɁA
        # �v���C�x�[�g���[�h��1�̐ݒ�s�̓X�L�b�v
        if ($settings[6] eq '1' && !$is_private_browsing_mode) {
            next;
        }

        # �z�X�g��UserAgent�̈�v����
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
            # ��v����z�X�g���Ȃ��ꍇ�̓X�L�b�v
            next;
        }
        @match_host_settings = uniq(@match_host_settings);

        # �X���b�h�쐬��/���X���ʂ̐ݒ�z��E�ϐ��ɗL���Ȑݒ���Z�b�g
        if ($type & THREAD_CREATE) {
            push(@thread_create_valid_settings, [@settings, \@match_host_settings]);
        }
        if ($type & RESPONSE) {
            push(@response_valid_settings, [@settings, \@match_host_settings]);
        }
    }
    $self{THREAD_CREATE_VALID_SETTINGS_ARRAY_REF} = \@thread_create_valid_settings;
    $self{RESPONSE_VALID_SETTINGS_ARRAY_REF} = \@response_valid_settings;

    # �����ΏۊO���[�U�[����
    foreach my $exempt_set_str (@{$firstpost_restrict_exempt_array_ref}) {
        # �ݒ蕶���񕪊����Đݒ�l���擾
        my @exempt_set = split(/:/, $exempt_set_str, 2);
        if (scalar(@exempt_set) < 1) {
            next;
        }

        # �z�X�g��UserAgent or CookieA or �o�^ID or ����ID�̂����ꂩ�ň�v�������ǂ����̃t���O
        my $host_useragent_or_cookiea_userid_historyid_matched_flg;

        # �z�X�g�EUserAgent��v����
        my ($host_useragent_match_array_ref)
            = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $exempt_set[0], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
        $host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($host_useragent_match_array_ref);

        # CookieA or �o�^ID or ����ID��v����
        if (!$host_useragent_or_cookiea_userid_historyid_matched_flg) {
            my ($cookiea_userid_historyid_match_array_ref)
                = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a_value, $user_id, $history_id, $exempt_set[1], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            $host_useragent_or_cookiea_userid_historyid_matched_flg ||= defined($cookiea_userid_historyid_match_array_ref);
        }

        # �z�X�g��UserAgent or CookieA or �o�^ID or ����ID�̂����ꂩ�ň�v�������߁A
        # �ΏۊO���[�U�[�t���O�𗧂Ă�
        if ($host_useragent_or_cookiea_userid_historyid_matched_flg) {
            $self{EXEMPT_USER} = 1;
            last;
        }
    }

    # �N���[�W����`
    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }

        # 1�ȏ�̈������^����ꂽ�ꍇ
        if (@_) {
            # �L�[�����ŏ��̈�������擾
            my $field = shift;

            # �L�[�����݂���ꍇ
            if (exists($self{$field})) {
                # �l�������Ƃ��ė^����ꂽ�ꍇ�A�Z�b�g����
                if (@_) {
                    $self{$field} = shift;
                }

                # �L�[�ɑΉ�����l��Ԃ�
                return $self{$field};
            }
        }
    };

    # �C���X�^���X���쐬
    my $instance = bless $closure, $class;

    # ����Cookie�����s�̏ꍇ�͔��s����
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

    # �X���b�h�쐬�ł��邩�ǂ����̃t���b�O
    my $new_thread_flag = $type & THREAD_CREATE;

    # ����Cookie�X�V���s�t���b�O
    my $update_cookie_flag;

    # CookieA�̒l�E�������E�������l�\�����擾
    my $cookie_a_value = $self->('COOKIE_A_VALUE');
    my $cookie_a_length = length($cookie_a_value);
    my $cookie_a_issue_datetime_num;
    if (defined($self->('COOKIE_A_VALUE'))
        && $cookie_a_value =~ /^(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[0-1]))_.._((?:[01]\d|2[0-3])[0-5]\d)$/
    ) {
        $cookie_a_issue_datetime_num = int("$1$2");
    }

    # �Q�Ƃ���L���ݒ�z�������
    my $valid_settings_array_ref
        = $new_thread_flag ? $self->('THREAD_CREATE_VALID_SETTINGS_ARRAY_REF') : $self->('RESPONSE_VALID_SETTINGS_ARRAY_REF');

    # Matcher::Utils�C���X�^���X�擾
    my Matcher::Utils $mu = $self->('MATCHER_UTILS_INSTANCE');

    # �����E���O�Ώ۔���
    foreach my $setting_array_ref (@{$valid_settings_array_ref}) {
        # �L���ݒ�s���擾
        my @settings = @{$setting_array_ref};

        # �������Ԑݒ���擾
        my $restrict_hour_setting = $settings[5];

        # ���X���ɃX���b�h����v����
        if (!$new_thread_flag) {
            # �X���b�h���̎w�肪�Ȃ��ꍇ�̓X�L�b�v
            if ($settings[3] eq '') {
                next;
            }

            # ��v����
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match(
                $thread_title, $settings[3], undef(), undef(), '*', Matcher::Utils::UTF8_FLAG_FORCE_ON
            )};
            if (!defined($title_match_array_ref)) {
                # ��v���Ȃ������ꍇ�̓X�L�b�v
                next;
            } elsif (scalar(grep { $_ ne '*' } map { ${$_}[0] } @{$title_match_array_ref}) > 0
                && $restrict_hour_setting > $self->('TITLE_MATCH_RESTRICT_HOUR')
            ) {
                # �u*�v�ȊO�Ń}�b�`�����X���b�h�^�C�g���̐ݒ�s�݂̂̍Œ��������ԍX�V
                $self->('TITLE_MATCH_RESTRICT_HOUR', $restrict_hour_setting);
            }
        }

        # �����Ώۃt���O���Z�b�g
        $self->('RESTRICTED', 1);

        # ���t�ɂ�鏜�O��
        if (!$self->('EXEMPT_USER') && defined($cookie_a_value)
            && $settings[1] =~ /^\d{2}(\d{2})\/(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[0-1]) ([01]\d|2[0-3]):([0-5]\d)$/
        ) {
            if ($cookie_a_length == 14 && defined($cookie_a_issue_datetime_num)) {
                # ���t�ɂ�鏜�O��̎w����� ���l�\�����쐬
                my $reference_datetime_num = int("$1$2$3$4$5");

                # CookieA���s���� �� ���t�ɂ�鏜�O��̎w����� �����ł���ꍇ�͏��O�Ώ�
                if ($cookie_a_issue_datetime_num < $reference_datetime_num) {
                    $self->('EXEMPT_USER', 1);
                }
            } elsif ($cookie_a_length == 12) {
                # CookieA�̌�����12���̏ꍇ�͑S�ď��O�Ώ�
                $self->('EXEMPT_USER', 1);
            }
        }

        # �Œ��������ԍX�V
        if ($restrict_hour_setting > $self->('RESTRICT_HOUR')) {
            $self->('RESTRICT_HOUR', $restrict_hour_setting);
            $update_cookie_flag = 1;
        }

        # �z�X�g��UserAgent���u*�v�ȊO�ň�v���Ă���Ƃ��́A
        # �ǉ�����z�X�g��ǉ��X�V����
        if (scalar(@{$settings[8]}) > 0) {
            my @current_add_judge_hosts = @{$self->('ADD_JUDGE_HOSTS')};
            my @updated_unique_add_judge_hosts = uniq(@current_add_judge_hosts, @{$settings[8]});
            if (scalar(@updated_unique_add_judge_hosts) != scalar(@current_add_judge_hosts)) {
                $self->('ADD_JUDGE_HOSTS', \@updated_unique_add_judge_hosts);
                $update_cookie_flag = 1;
            }
        }
    }

    # ����Cookie�̍X�V���s��K�v�ɉ����čs��
    if ($update_cookie_flag) {
        issue_cookie($self);
    }
}

sub get_left_hours_of_restriction {
    my ($self) = @_;
    if (!defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance variable.');
    }

    # �����c�莞�Ԃ��v�Z���ĕԂ�
    my $hours_of_restriction = get_hours_of_restriction($self);
    if ($self->('RESTRICTED') && !$self->('EXEMPT_USER') && $hours_of_restriction > 0) {
        # ����A�N�Z�X����+�������Ԃ��猻�ݓ��������Z���āA�����c�莞�Ԃ��Z�o
        # (��������������59�b�܂ł𐧌����ԂɊ܂߂�̂ŁA��������+1�������Z���Ă���A���ݓ����Ƃ̍��������)
        my $left_time = ($self->('TIME') + ($hours_of_restriction * ONE_HOUR) + ONE_MINUTE) - $self->('NOW');
        my $left_hours = ceil($left_time->hours); # �c�莞�Ԃ��擾���A�����_�ȉ���؂�グ (ex. 0.2h -> 1h)
        if ($left_hours >= 0) {
            # 0���Ԉȏ�c���Ă���ꍇ�͂��̎��Ԃ�Ԃ�
            # (�����J�n��ŏ���1���Ԃ�1����1���͈̔͂���邽�߁A�����_�ȉ��؂�グ��1���ԑ����\������Ă��܂����߁A
            # �΍�Ƃ��āA�����c�莞�ԂƐ������Ԃ̂ǂ��炩�����������g�p����)
            return min($left_hours, $hours_of_restriction);
        } else {
            # �}�C�i�X���Ԃ͐��������������߂Ȃ̂ŁA0��Ԃ�
            return 0;
        }
    } else {
        # �����ΏۊO�Ȃ̂ŁA0��Ԃ�
        return 0;
    }
}

sub get_first_access_datetime {
    my $self = shift;
    if (!defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance variable.');
    }

    # ����Cookie���s�������t�H�[�}�b�g
    my $value = format_issue_datetime($self);

    # CP932�G���R�[�h�ɕϊ����ĕԂ�
    return $enc_cp932->encode($value);
}

sub get_hours_of_restriction {
    my $self = shift;
    if (!defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance variable.');
    }

    # �������Ԃ�Ԃ�
    # (�X���b�h�^�C�g���ŁA*����������v���������ꍇ�̍Œ��������Ԃ�D��)
    return $self->('TITLE_MATCH_RESTRICT_HOUR') > 0 ? $self->('TITLE_MATCH_RESTRICT_HOUR') : $self->('RESTRICT_HOUR');
}

sub value {
    my $self = shift;
    my ($encode_flag) = @_;
    if (!defined(blessed($self)) || !$self->isa('FirstCookie')) {
        confess('call me only in instance variable.');
    }

    # Cookie���s����������쐬
    my $value = format_issue_datetime($self);

    # �������Ԃ��ݒ肳��Ă��鎞�́A�t���O�����Ɛ������ԏ���t��
    my $restrict_hour = $self->('RESTRICT_HOUR');
    if ($restrict_hour > 0) {
        $value .= $restrict_time_char . $restrict_hour;
    }

    # �ǉ�����z�X�g�����݂���ꍇ�́A�t���O�����ƒǉ�����z�X�g�������t��
    my @unique_add_judge_hosts = uniq(@{$self->('ADD_JUDGE_HOSTS')});
    if (scalar(@unique_add_judge_hosts) > 0) {
        $value .= $additional_hosts_char . join(',', @unique_add_judge_hosts);
    }

    if ($encode_flag) {
        # CP932�G���R�[�h�ɕϊ����ĕԂ�
        return $enc_cp932->encode($value);
    } else {
        # �����G���R�[�h�̂܂ܕԂ�
        return $value;
    }
}

1;
