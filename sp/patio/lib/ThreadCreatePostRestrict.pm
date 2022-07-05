package ThreadCreatePostRestrict;
use strict;

use open IO => ':encoding(cp932)';

use Encode qw();
use Carp qw(croak confess);
use Scalar::Util qw(blessed);
use List::MoreUtils qw(uniq);

use Matcher::Utils;

my Encode::Encoding $enc_cp932 = defined($main::enc_cp932) ? $main::enc_cp932 : Encode::find_encoding('cp932');

# ���茋�ʒ萔��`
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
};

# �O���t�@�C���Ŏw�肳�ꂽ������CookieA���s�������r���A
# ���O�Ώۂł��邩�ǂ�����Ԃ��T�u���[�`��
sub is_except_cookie_a_issue_datetime {
    my ($reference_datetime_str, $cookie_a_length, $cookie_issue_datetime_num) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }

    if ($cookie_a_length != 12 && $cookie_a_length != 14) {
        # CookieA�̌������������Ȃ��ꍇ�́A���O�Ώۂł͂Ȃ�
        return;
    }

    if ($reference_datetime_str !~ /^\d{2}(\d{2})\/(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[0-1]) ([01]\d|2[0-3]):([0-5]\d)$/) {
        # �O���t�@�C���w��������A�z�肷��t�H�[�}�b�g�łȂ��ꍇ�͏��O�Ώۂł͂Ȃ�
        return;
    }

    # CookieA�̒l��12���̏ꍇ�͂��ׂď��O�Ώ�
    if ($cookie_a_length == 12) {
        return 1;
    }

    # �O���t�@�C���w����� ���l�\�����쐬
    my $reference_datetime_num = int("$1$2$3$4$5");

    # CookieA���s���� �� �O���t�@�C���w����� �����ł��邩�ǂ�����Ԃ�
    return $cookie_issue_datetime_num < $reference_datetime_num;
}

# �O���t�@�C���Ŏw�肳�ꂽCookieA,�o�^ID,����ID�Ɋ��S��v����
# ���O�Ώۂł��邩�ǂ�����Ԃ��T�u���[�`��
sub is_except_cookie_a_user_id_history_id {
    my ($target_str, $cookie_a, $user_id, $history_id) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }

    if ($target_str eq '') {
        # �Ώېݒ蕶���񂪋�̏ꍇ�͏��O�Ώ۔�����s��Ȃ�
        return;
    }

    # �u*�v���w�肳��A�o�^ID������ID�̂����ꂩ�����݂���ꍇ�͂��ׂď��O�Ώ�
    if ($target_str eq '*' && ($user_id ne '' || $history_id ne '')) {
        return 1;
    }

    # ��v����Ώ� CookieA, �o�^ID, ����ID���n�b�V���̃L�[�Ƃ��Ď擾
    my %value_existent_elements = map { $_ => undef } grep { $_ ne '' } ($cookie_a, $user_id, $history_id);
    if (scalar(keys(%value_existent_elements)) == 0) {
        # ��v����Ώۂ��Ȃ��ꍇ�́A���O�Ώ۔�����s��Ȃ�
        return;
    }

    # �w�蕶������u,�v�ŕ���
    my @targets = grep { $_ ne '' } split(/,/, $target_str, -1);

    # ��v����Ώۃn�b�V���̃L�[�ɑ��݂��邩�ǂ�����
    # ���S��v������s���A��v�������ǂ�����Ԃ�
    foreach my $target (@targets) {
        if (exists($value_existent_elements{$target})) {
            # ��v����
            return 1;
        }
    }
    # ������ɂ���v���Ȃ�����
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

    # Matcher::Utils�C���X�^���X�擾
    my Matcher::Utils $mu = $matcher_utils_instance;

    # CookieA �������擾
    my $cookie_a_length = length($cookie_a);

    # CookieA���s���� ���l�\�����쐬 (���݂�CookieA���s�`���Ɍ���)
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

    # �O���t�@�C�����p�[�X
    my $thread_create_restrict_status = RESULT_NO_RESTRICTED; # �X���b�h�쐬�����@�\ �����Ώ۔��茋��
    my @valid_setting_pairs_of_post_restrict_by_thread_title; # �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\ �L���ݒ�z��
    my $disable_setting_char = $enc_cp932->decode('��');

    # �O���t�@�C���I�[�v��
    open(my $setting_fh, '<', $setting_filepath) || croak("Open error: $setting_filepath");
    flock($setting_fh, 1) || croak("Lock error: $setting_filepath");
    $self{SETTING_FH} = $setting_fh;

    # �w�b�_�s(2�s)�ǂݔ�΂�
    <$setting_fh>;
    <$setting_fh>;

    # �X���^�C�ɂ�鐧���̏��O(�w��) �̏��������������`
    my $thread_title_post_restrict_exemption_condition_split_regex;
    {
        my $decoded_char = $enc_cp932->decode('��');
        $thread_title_post_restrict_exemption_condition_split_regex = qr/$decoded_char/;
    }

    # �L���Ȑݒ�s��ǂݍ���
    while (my $line = <$setting_fh>) {
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @settings = split(/\^/, $line, -1);
        if (scalar(@settings) != 20 || $settings[1] eq $disable_setting_char) {
            # 20��ł͂Ȃ����O�s�A�������́A������Ɂ��̗�̓X�L�b�v
            next;
        }

        # �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�E�v���C�x�[�g���[�h�ECookieA�̗L���E���Ԕ͈͎w��E���Ԏw��E�X���쐬�����E�X���^�C�ɂ�鐧���ɂ��āA
        # �u-�v���󕶎���ɒu��������
        foreach my $i (2 .. 7, 10, 12) {
            $settings[$i] =~ s/^-$//;
        }

        # �v���C�x�[�g���[�h��1�̏ꍇ�ɑΏ۔���
        my $private_browsing_mode_match_flag;
        if ($settings[4] eq '1') {
            if ($is_private_browsing_mode) {
                $private_browsing_mode_match_flag = 1;
            } else {
                next;
            }
        }

        # CookieA�̗L����1�̏ꍇ�ɑΏ۔���
        # (�����s�̏ꍇ���Ώۂ̂��߁A���s����Ă���ꍇ�̓X�L�b�v)
        if ($settings[5] eq '1' && $cookie_a_instance->is_issued()) {
            next;
        }

        # �u�z�X�g��UserAgent�v���uCookieA or �o�^ID or ����ID�v�̂����ꂩ�ň�v�������ǂ����̃t���O
        my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;

        # �z�X�g��UserAgent�̈�v����
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

        # CookieA or �o�^ID or ����ID�̈�v����
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

        # �u�z�X�g��UserAgent�v���uCookieA or �o�^ID or ����ID�v��
        # �ǂ��炩�ň�v���Ă��Ȃ��Ƃ��́A�X�L�b�v
        if ($host_useragent_or_cookiea_userid_historyid_matched_flg == 0) {
            next;
        }

        # ���Ԕ͈͎w��̈�v����
        my @match_time_range_array;
        if ($settings[6] ne '') {
            if ($mu->is_in_time_range($settings[6], undef())) {
                @match_time_range_array = ($settings[6]);
            } else {
                next;
            }
        }

        # ���Ԏw��E�o�ߎ��Ԃ̈�v����
        if ($settings[7] ne '' && $settings[8] ne '') {
            if (!$mu->is_within_validity_period($settings[7], $settings[8], undef())) {
                next;
            }
        }

        # �X���b�h�쐬�����@�\�̔���
        if ($settings[10] ne '') {
            # �����^�C�v���m��
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

            # �����Ώۂ������ꍇ�A
            # �X���쐬�����̏��O(���t) �������� �X���쐬�����̏��O(�w��) �̑Ώۂł��邩�ǂ�������
            if ($currentset_thread_create_restrict_status != RESULT_NO_RESTRICTED
                && (is_except_cookie_a_issue_datetime($settings[15], $cookie_a_length, $cookie_a_issue_datetime_num)
                    || is_except_cookie_a_user_id_history_id($settings[16], $cookie_a, $user_id, $history_id)
                )
            ) {
                $currentset_thread_create_restrict_status = RESULT_NO_RESTRICTED;
            }

            # ���茋�ʂ𓝍�
            $thread_create_restrict_status |= $currentset_thread_create_restrict_status;
        }

        # �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\ �L���ݒ��ۑ�
        if ($settings[12] ne '' && $settings[13] ne '') {
            # �����^�C�v���m��
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

            # �����Ώۂ������ꍇ�A
            # �X���^�C�ɂ�鐧���̏��O(���t) �������� �X���^�C�ɂ�鐧���̏��O(�w��) �̑Ώۂł��邩�ǂ�������
            my @exempt_thread_titles; # ���O�X���b�h�^�C�g���ݒ�z��
            if (defined($restrict_type)) {
                if (is_except_cookie_a_issue_datetime($settings[18], $cookie_a_length, $cookie_a_issue_datetime_num)) {
                    # �X���^�C�ɂ�鐧���̏��O(���t) �̑Ώۂ������ꍇ�A���O
                    $restrict_type = undef;
                } else {
                    # �X���^�C�ɂ�鐧���̏��O(�w��) �Ώ۔���

                    # �u���v�ɂ�镡���������[�v
                    foreach my $condition_str (split($thread_title_post_restrict_exemption_condition_split_regex, $settings[19])) {
                        # CookieA/�o�^ID/����ID�ƃX���b�h�^�C�g���̑Ώە�����𕪊�
                        my ($target_cookie_a_user_id_history_ids, $target_thread_title) = split(/<>/, $condition_str, 2);

                        # �������������Ȃ��ꍇ��ACookieA/�o�^ID/����ID����v���Ȃ��ꍇ�̓X�L�b�v
                        if (!defined($target_cookie_a_user_id_history_ids)
                            || (defined($target_thread_title) && $target_thread_title eq '')
                            || !is_except_cookie_a_user_id_history_id($target_cookie_a_user_id_history_ids, $cookie_a, $user_id, $history_id)
                        ) {
                            next;
                        }

                        # �ΏۃX���b�h�^�C�g���m��
                        if (!defined($target_thread_title)) {
                            # �w�肪�Ȃ��ꍇ�́A�X���b�h�^�C�g����̒l�����O�ΏۂƂ���
                            $target_thread_title = $settings[13];
                        }

                        # ���O�X���b�h�^�C�g���ݒ�z��ɒǉ�
                        push(@exempt_thread_titles, $target_thread_title);
                    }
                }
            }

            # �����^�C�v���m��ł����ꍇ�̂݁A�L���ݒ�Ƃ��Ĕz��ɒǉ�
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

    # �N���[�W����`
    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }
        arg_check(1, [''], @_);

        # �����Ƃ��ė^����ꂽ�L�[�ɑΉ�����l��Ԃ�
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

    # �O���t�@�C���n���h�� �N���[�Y
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

    # Matcher::Utils�C���X�^���X�擾
    my Matcher::Utils $mu = $self->('MATCHER_UTILS_INSTANCE');

    my $status = RESULT_NO_RESTRICTED;

    # �X���b�h�^�C�g���ɂ�鏑�����ݐ����@�\�̃X���b�h�쐬�҂̏��O�@�\ ����
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

    # �X���b�h������
    #
    # �X���^�C�ɂ�鐧���̏��O(�w��)�̑Ώۂł͂Ȃ��X���b�h����ΏۂɁA
    # �X���^�C�ɂ�鐧���̈�v������s���āA�����^�C�v���m�肳����
    foreach my $setting_pair (@{$self->('VALID_SETTING_PAIRS_OF_POST_RESTRICT_BY_THREAD_TITLE')}) {
        my ($restrict_type, $target_thread_title, $exempt_thread_title) = @{$setting_pair};

        # �X���^�C�ɂ�鐧���̏��O(�w��)�̑Ώ۔���
        my ($exempt_result_array_ref) =
            @{ $mu->get_matched_thread_title_to_setting_and_whether_its_not_match(
                $thread_title, $exempt_thread_title, undef(), undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON
            ) };
        if (defined($exempt_result_array_ref)) {
            next;
        }

        # �X���^�C�ɂ�鐧���̈�v����
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
