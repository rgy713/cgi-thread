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

my $disable_setting_char = $enc_cp932->decode('��');
my $multiple_submissions_count_log_delimiter = '<>';
my $old_thread_age_count_log_delimiter = '<>';

my $under_threshold_char = $enc_cp932->decode('��');
my $over_threshold_char = $enc_cp932->decode('��');

# ���茋�ʒ萔��`
use constant {
    RESULT_ALL_PASSED                      => 0,
    RESULT_THREAD_CREATE_SUPPRESS_REQUIRED => 1,
    RESULT_REDIRECT_REQUIRED               => 1 << 1
};

# �����������݋֎~���O �w�b�_�[��`
my @log_header = map { $enc_cp932->decode($_); } (
    '����', 'CookieA���s', '�v���C�x�[�g����', '��v����', '���Ԏw��', '�X�e�[�^�X',
    '�X���^�C���O', '���O', '����', 'URL', '�J�e�S��', '��', '��v�X���^�C', '�X���^�C�����̏��O',
    '��v�X���^�C�i�}���j', '��v���X�i�}���j', '��', '��v���O', '��', '������', '�Ώۂ̃��X',
    '��v���X', '���������O', '�w�背�X�Ԃ܂ł̈�v���X', '���������O', '�����񃌃X', '�ÃX��age', '��',
    '�X���쐬���̃X���^�C�ɂ�郌�X�̏��O�i�X���j', '�X���쐬���̃X���^�C�ɂ�郌�X�̏��O�i���X�j',
    '�X���^�C�ɂ�郌�X�̏��O�i�X���j', '�X���^�C�ɂ�郌�X�̏��O�i���X�j', '�w�背�X�܂ŏ��O', '��',
    '�X���쐬���̃X���^�C������v', '�X���쐬���̋�����v���X�i�X���j', '�X���쐬���̋�����v���X�i���X�j',
    '�X���^�C�ɂ�鋭����v���X�i�X���j', '�X���^�C�ɂ�鋭����v���X�i���X�j', '�摜�A�b�v', '��',
    '��vCookieA', '��v�o�^ID', '��v����ID', '��v�z�X�g', '��vUserAgent', '��vMD5', '��v�摜�R�����g', '��',
    '�X���^�C', '���O', '���X���e', '�摜����', '�v���C�x�[�g',
    'CookieA', '�o�^ID', '����ID', '�z�X�g', 'UserAgent', '�^�C���X�^���v', 'ID'
);

# �����������݋֎~���O 2�s�ڃw�b�_�[��`
my $log_second_header_row = $enc_cp932->decode(
    'AA,yy,BB,CC,zz,DD,ww,EE,FF,GG,HH,��,II,JJ,KK,LL,��,MM,��,xx,NN,OO,WW,PP,aaa,QQ,RR,��,SS,TT,YY,VV,bbb,��,XX,YY,ZZ,aa,bb,cc,��,dd,ee,ff,gg,hh,ii,jj,��,kk,ll,mm,nn,oo,pp,qq,rr,ss,tt,uu,vv'
);

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

    # Matcher::Utils�C���X�^���X�擾
    my Matcher::Utils $mu = $matcher_utils_instance;

    # �X���b�h�^�C�g��/�J�e�S�����u�������Z�b�g�擾
    my @category_set;
    foreach my $conv_set_str (@{$category_set_array_ref}) {
        my $decoded_conv_set_str = $enc_cp932->decode($conv_set_str);
        my ($keyword, $category) = split(/:/, $decoded_conv_set_str, 2);
        if ($keyword eq '' || $category eq '') {
            next;
        }
        push(@category_set, [$keyword, $category]);
    }

    # �X���b�hNo�������������݋֎~�@�\�̃��X���������œ��삷��@�\ �������Ԕz��쐬
    my @thread_number_res_target_hold_hours = (
        undef, # type�l�����̂܂�index�Ƃ��邽�߂�dummy�v�f
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

    # �O���t�@�C�����p�[�X���A�L���Ȑݒ��ǂݍ���
    my @validsetting_and_userinfo_matchresult;

    # �O���t�@�C���I�[�v��
    open(my $setting_fh, '<', $setting_filepath) || croak("Open error: $setting_filepath");
    flock($setting_fh, 1) || croak("Lock error: $setting_filepath");
    $self{SETTING_FH} = $setting_fh;

    # �w�b�_�s(2�s)�ǂݔ�΂�
    <$setting_fh>;
    <$setting_fh>;

    # �O���t�@�C�����p�[�X���A�L���Ȑݒ��ǂݍ���
    while (my $line = <$setting_fh>) {
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @settings = split(/\^/, $line, - 1);
        if (scalar(@settings) != 38 || $settings[1] eq $disable_setting_char) {
            # 38��ł͂Ȃ����O�s�A�������́A������Ɂ��̗�̓X�L�b�v
            next;
        }

        # �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�E�v���C�x�[�g���[�h�E���Ԕ͈͎w��E���Ԏw��E�摜��ɂ��āA
        # �u-�v���󕶎���ɒu��������
        foreach my $i (2 .. 6, 31) {
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

        # �u�z�X�g��UserAgent�v���uCookieA or �o�^ID or ����ID�v�̂����ꂩ�ň�v�������ǂ����̃t���O
        my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;

        # �z�X�g��UserAgent�̈�v����
        my @host_useragent_match_array = ([], []);
        if ($settings[2] ne '') {
            my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $settings[2], ['**', '**'], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (defined($host_useragent_match_array_ref)) {
                @host_useragent_match_array = @{$host_useragent_match_array_ref};
                $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
            }
        }

        # CookieA or �o�^ID or ����ID�̈�v����
        my @cookiea_userid_historyid_match_array = ([], [], []);
        if ($settings[3] ne '') {
            my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $settings[3], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
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
        if ($settings[5] ne '') {
            if ($mu->is_in_time_range($settings[5], undef())) {
                @match_time_range_array = ($settings[5]);
            } else {
                next;
            }
        }

        # ���Ԏw��E�o�ߎ��Ԃ̈�v����
        if ($settings[6] ne '' && $settings[7] ne '') {
            if (!$mu->is_within_validity_period($settings[6], $settings[7], undef())) {
                next;
            }
        }

        # �ݒ�l�Ɓu�z�X�g��UserAgent�v�E�uCookieA or �o�^ID or ����ID�v�E�u���Ԕ͈́v�̈�v���ʂ�
        # �L���ݒ�E���[�U�[���z��Ɋi�[
        push(@validsetting_and_userinfo_matchresult,
            [
                \@settings,
                $host_useragent_match_array[0], # �z�X�g
                $host_useragent_match_array[1], # ��vUserAgent
                $cookiea_userid_historyid_match_array[0], # ��vCookieA
                $cookiea_userid_historyid_match_array[1], # ��v�o�^ID
                $cookiea_userid_historyid_match_array[2], # ��v����ID
                \@match_time_range_array, # ��v���Ԕ͈�
                $private_browsing_mode_match_flag # �v���C�x�[�g�u���E�W���O���[�h�Ώېݒ�ň�v�������ǂ���
            ]
        );
    }
    $self{VALIDSETTING_AND_USERINFO_MATCHRESULT} = \@validsetting_and_userinfo_matchresult;

    # �����������݋֎~���O�I�[�v��
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

    # �����������݋֎~���O�ɓ���z�X�g/CookieA/�o�^ID/����ID���܂܂�邩�`�F�b�N
    # (���O�t�@�C���V�K�쐬���ɂ̓`�F�b�N���Ȃ�)
    my $read_log_contents = '';
    my ($read_skip_flag, $log_exist_host_flag, $log_exist_cookiea_flag, $log_exist_userid_flag, $log_exist_historyid_flag);
    if (!$new_log_flag) {
        # ���O ���ڃC���f�b�N�X�擾
        my ($title_exempt_index, $exempt_index, $cookiea_index, $userid_index, $historyid_index, $host_index, $timestamp_index);
        {
            my ($find_title_exempt, $find_exempt, $find_cookiea, $find_userid, $find_historyid, $find_host, $find_timestamp)
                = map { $enc_cp932->decode($_) } ('�X���^�C���O', '���O', 'CookieA', '�o�^ID', '����ID', '�z�X�g', '�^�C���X�^���v');
            ($title_exempt_index) = grep { $log_header[$_] eq $find_title_exempt } 0 .. $#log_header;
            ($exempt_index) = grep { $log_header[$_] eq $find_exempt } 0 .. $#log_header;
            ($cookiea_index) = grep { $log_header[$_] eq $find_cookiea } 0 .. $#log_header;
            ($userid_index) = grep { $log_header[$_] eq $find_userid } 0 .. $#log_header;
            ($historyid_index) = grep { $log_header[$_] eq $find_historyid } 0 .. $#log_header;
            ($host_index) = grep { $log_header[$_] eq $find_host } 0 .. $#log_header;
            ($timestamp_index) = grep { $log_header[$_] eq $find_timestamp } 0 .. $#log_header;
        }

        # �z�X�g�����E���_�C���N�g����v�f�ǉ� �Ώۃz�X�g�ɒ��Ԉ�v�������̓t���O�𗧂Ă�
        my $ignore_host_in_log_matching_flag;
        foreach my $partial_hostname (@{$additional_match_required_host_array_ref}) {
            if (index($host, $partial_hostname) != - 1) {
                $ignore_host_in_log_matching_flag = 1;
                last;
            }
        }

        # �u���O�v��v�̂��߁A�����G���R�[�h�ɕϊ�
        my $decoded_exempt_str = $enc_cp932->decode('���O');

        # �����������݋֎~���O �ǂݍ��݁E����
        seek($log_fh, 0, 0); # �t�@�C���|�C���^��擪�Ɉړ�
        <$log_fh>; # �擪�s�ǂݔ�΂�
        <$log_fh>; # 2�s�ړǂݔ�΂�
        while (my $line = <$log_fh>) {
            $line =~ s/(?:\r\n|\r|\n)$//;
            my @row = split(/,/, $line);

            # �s���s�E�����������Ԃ��o�߂������O�s�𔻒肩�珜�O
            if (scalar(@row) != scalar(@log_header)
                || ($log_delete_time != 0 && $row[$timestamp_index] + $log_delete_time < $time)) {
                $read_skip_flag ||= 1;
                next;
            }

            # �X���^�C���O��Ə��O�񂪁u���O�v�ł͂Ȃ����O�s�̂ݔ�����s��
            if ($row[$title_exempt_index] ne $decoded_exempt_str && $row[$exempt_index] ne $decoded_exempt_str) {
                # ���S��v����z�X�g�������������̓t���O�𗧂Ă�
                if (!$ignore_host_in_log_matching_flag && $row[$host_index] eq $host) {
                    $log_exist_host_flag ||= 1;
                }

                # ���S��v����CookieA�������������̓t���O�𗧂Ă�
                if ($row[$cookiea_index] ne '' && $row[$cookiea_index] eq $cookie_a) {
                    $log_exist_cookiea_flag ||= 1;
                }

                # ���S��v����o�^ID�����������Ƃ��̓t���O�𗧂Ă�
                if ($row[$userid_index] ne '' && $row[$userid_index] eq $user_id) {
                    $log_exist_userid_flag ||= 1;
                }

                # ���S��v���鏑��ID�����������Ƃ��̓t���O�𗧂Ă�
                if ($row[$historyid_index] ne '' && $row[$historyid_index] eq $history_id) {
                    $log_exist_historyid_flag ||= 1;
                }
            }

            # ���O�s���c��
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

    # �X���b�hNo�������������݋֎~�@�\�̃��X���������œ��삷��@�\
    # ���O�t�@�C���p�[�X����
    my @thread_number_res_target;
    if (-s $thread_number_res_target_log_path > 2) {
        # ���O�t�@�C���ǂݍ��݁E�p�[�X����
        my $json_log_fh;
        if (open($json_log_fh, '<:utf8', $thread_number_res_target_log_path) && flock($json_log_fh, 1)) {
            # ���O�t�@�C������x�ɓǂݍ���
            seek($json_log_fh, 0, 0);
            local $/;
            my $json_log_contents = <$json_log_fh>;
            close($json_log_fh);

            # JSON�p�[�X���s�� (���e���ُ�̏ꍇ�̓X�L�b�v)
            eval {
                my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
                if (ref($json_parsed_ref) eq 'ARRAY') {
                    @thread_number_res_target = @{$json_parsed_ref};
                }
            };
        }
    }
    $self{THREAD_NUMBER_RES_TARGET_ARRAY_REF} = \@thread_number_res_target;

    # �X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\
    # ���O�t�@�C���p�[�X����
    my @thread_title_res_target;
    if (-s $thread_title_res_target_log_path > 2) {
        # ���O�t�@�C���ǂݍ��݁E�p�[�X����
        my $json_log_fh;
        if (open($json_log_fh, '<:utf8', $thread_title_res_target_log_path) && flock($json_log_fh, 1)) {
            # ���O�t�@�C������x�ɓǂݍ���
            seek($json_log_fh, 0, 0);
            local $/;
            my $json_log_contents = <$json_log_fh>;
            close($json_log_fh);

            # JSON�p�[�X���s�� (���e���ُ�̏ꍇ�̓X�L�b�v)
            eval {
                my $json_parsed_ref = JSON::XS->new()->utf8(0)->decode($json_log_contents);
                if (ref($json_parsed_ref) eq 'ARRAY') {
                    @thread_title_res_target = @{$json_parsed_ref};
                }
            };
        }
    }
    $self{THREAD_TITLE_RES_TARGET_ARRAY_REF} = \@thread_title_res_target;

    # �����񓊍e���̎����������݋֎~�@�\
    # ���O�t�@�C���p�[�X����
    my $multiple_submissions_count_log_fh;
    my @multiple_submissions_validlog;
    open($multiple_submissions_count_log_fh, '+<', $multiple_submissions_count_log_path)
        || open($multiple_submissions_count_log_fh, '>', $multiple_submissions_count_log_path)
        || croak("Open error: $multiple_submissions_count_log_path");
    flock($multiple_submissions_count_log_fh, 2) || croak("Lock error: $multiple_submissions_count_log_path");
    seek($multiple_submissions_count_log_fh, 0, 0);
    while (my $line = <$multiple_submissions_count_log_fh>) {
        # ���s�����������A<>�ŕ���
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @log = split(/$multiple_submissions_count_log_delimiter/, $line);

        # 5���ڑ��݂��Ȃ����A�������Ԃ��o�߂��Ă��郍�O�s�̓X�L�b�v
        if (scalar(@log) != 5  || ($log[4] + $multiple_submissions_log_hold_minutes * 60) < $time) {
            next;
        }

        # �L�����O�z��ɒǉ�
        push(@multiple_submissions_validlog, \@log);
    }
    seek($multiple_submissions_count_log_fh, 0, 0);
    $self{MULTIPLE_SUBMISSIONS_COUNT_LOG_FH} = $multiple_submissions_count_log_fh;
    $self{MULTIPLE_SUBMISSIONS_VALIDLOG_ARRAY_REF} = \@multiple_submissions_validlog;

    # �����񓊍e���̎����������݋֎~�@�\
    # ���[�U�[�J�E���g���O �z�X�g�L�^����
    my $multiple_submissions_log_record_host_flag = 1;
    foreach my $exclude_host (@{$multiple_submissions_log_not_record_host_array_ref}) {
        if (index($host, $exclude_host) >= 0) {
            $multiple_submissions_log_record_host_flag = 0;
            last;
        }
    }
    $self{MULTIPLE_SUBMISSIONS_LOG_RECORD_HOST_FLAG} = $multiple_submissions_log_record_host_flag;

    # �ÃX��age�̎����������݋֎~�@�\
    # ���O�t�@�C���p�[�X����
    my $old_thread_age_count_log_fh;
    my @old_thread_age_validlog;
    open($old_thread_age_count_log_fh, '+<', $old_thread_age_count_log_path)
        || open($old_thread_age_count_log_fh, '>', $old_thread_age_count_log_path)
        || croak("Open error: $old_thread_age_count_log_path");
    flock($old_thread_age_count_log_fh, 2) || croak("Lock error: $old_thread_age_count_log_path");
    seek($old_thread_age_count_log_fh, 0, 0);
    while (my $line = <$old_thread_age_count_log_fh>) {
        # ���s�����������A<>�ŕ���
        $line =~ s/(?:\r\n|\r|\n)$//;
        my @log = split(/$old_thread_age_count_log_delimiter/, $line);

        # 5���ڑ��݂��Ȃ����A�������Ԃ��o�߂��Ă��郍�O�s�̓X�L�b�v
        if (scalar(@log) != 5  || ($log[4] + $old_thread_age_log_hold_minutes * 60) < $time) {
            next;
        }

        # �L�����O�z��ɒǉ�
        push(@old_thread_age_validlog, \@log);
    }
    seek($old_thread_age_count_log_fh, 0, 0);
    $self{OLD_THREAD_AGE_COUNT_LOG_FH} = $old_thread_age_count_log_fh;
    $self{OLD_THREAD_AGE_VALIDLOG_ARRAY_REF} = \@old_thread_age_validlog;

    # �ÃX��age�̎����������݋֎~�@�\
    # �ÃX��age���[�U�[�J�E���g���O �z�X�g�L�^����
    my $old_thread_age_log_record_host_flag = 1;
    foreach my $exclude_host (@{$old_thread_age_log_not_record_host_array_ref}) {
        if (index($host, $exclude_host) >= 0) {
            $old_thread_age_log_record_host_flag = 0;
            last;
        }
    }
    $self{OLD_THREAD_AGE_LOG_RECORD_HOST_FLAG} = $old_thread_age_log_record_host_flag;

    # �N���[�W����`
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
            # �����Ƃ��ė^����ꂽ�L�[�ɑΉ�����l��Ԃ�
            return $self{$key};
        } else {
            # �����Ƃ��ė^����ꂽ�L�[�ɒl���Z�b�g���A���̒l�����̂܂ܕԂ�
            my $set_value = shift;
            $self{$key} = $set_value;
            return $self{$key};
        }
    };

    return bless $closure, $class;
}

sub DESTROY {
    my $self = shift;

    # �O���t�@�C���n���h�� �N���[�Y
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

    # ���O�ǂݍ��݂�1�x�����s��Ȃ����߁A������̔�����s�����Ƃ͑z�肵�Ă��Ȃ�
    if ($self->('CALL_CHECK_FLAG')) {
        confess('this subroutine can be called only once.');
    } else {
        $self->('CALL_CHECK_FLAG', 1);
    }

    # Matcher::Utils�C���X�^���X�擾
    my Matcher::Utils $mu = $self->('MATCHER_UTILS_INSTANCE');

    my ($private_browsing_mode_matched_flag);

    # �X���b�h�^�C�g�� �J�e�S�����v����E�u������
    my $category = '';
    my $category_removed_title = $title;
    foreach my $conv_set_ref (@{$self->('CATEGORY_SET')}) {
        my ($keyword, $cat) = @{$conv_set_ref};
        my $capture_regex = '^(.*)' . quotemeta($keyword) . '$';
        if ($title =~ /$capture_regex/) {
            # �J�e�S�������Z�b�g
            $category = $cat;
            # �X���b�h�����J�e�S���������������̂Œu������
            $category_removed_title = $1;
            last;
        }
    }

    # >>1�̃��X���e�����o��
    my $first_res = ${${$log_array_ref}[1]}[4];

    # ���X���������擾
    my $res_length = do {
        my $normalized_res = $res;
        $normalized_res =~ s/<br>//g;
        $normalized_res = HTML::Entities::decode($normalized_res);
        length($normalized_res);
    };

    # �O���t�@�C���Őݒ���`���Ă��鎩���������݋֎~�@�\�֘A�̔���
    # ��v���ʔz��̒�`
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
    # �����������݋֎~�@�\(���X)�ň�v�����ݒ�s�̕��������O�ݒ�̔z��̒�`
    my @valid_exempt_res_length_settings;
    foreach my $validsetting_and_userinfo_matchresult_array_ref (@{$self->('VALIDSETTING_AND_USERINFO_MATCHRESULT')}) {
        # �s�̐ݒ�̂����ꂩ�Ɉ�v�������ǂ����̃t���O
        my $match_flag;

        # �ݒ���擾
        my @settings = @{${$validsetting_and_userinfo_matchresult_array_ref}[0]};

        # �X���b�h�쐬�}���@�\�E�����������݋֎~�@�\�̃X���b�h�쐬���̃��X�̏��O�@�\
        # ���荀��: �X���b�h�^�C�g��, ���X���e
        # (�V�K�X���b�h�쐬���̂ݔ�����s��)
        if ($new_thread_flag && $settings[20] ne '' && $settings[21] ne '') {
            # �X���b�h�^�C�g���ƃ��X���e�̈�v����
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[20]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[21]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            # ���������O���� (�w�肪�Ȃ��ꍇ�͔�����s��Ȃ�)
            my $res_length_exempt_match_or_pass_flag = $settings[22] ne '' ? $settings[22] <= $res_length : 1;

            if (defined($title_match_array_ref) && defined($res_match_array_ref) && $res_length_exempt_match_or_pass_flag) {
                # ��v�����X���b�h�^�C�g���E���X�����o��
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @match_res_exempt_on_thread_create = (
                    [uniq(@{$match_res_exempt_on_thread_create[0]}, @title_match_array)], # ��v�X���b�h�^�C�g��
                    [uniq(@{$match_res_exempt_on_thread_create[1]}, @res_match_array)]    # ��v���X���e
                );

                # �s�ݒ��v�t���O�𗧂Ă�
                $match_flag ||= 1;
            }
        }

        # �X���b�h�쐬�}���@�\�E�����������݋֎~�@�\(���ɃX���b�h�^�C�g������)�̏��O�@�\
        # ���荀��: �X���b�h�^�C�g��
        # (�V�K�X���b�h�쐬���̂ݔ�����s��)
        if ($new_thread_flag && $settings[19] ne '') {
            # �X���b�h�^�C�g���ƃ��X���e�̈�v����
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[19]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref)) {
                # ��v�����X���b�h�^�C�g�������o��
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @match_title_exempt_on_thread_create = uniq(@match_title_exempt_on_thread_create, @title_match_array);

                # �s�ݒ��v�t���O�𗧂Ă�
                $match_flag ||= 1;
            }
        }

        # �����������݋֎~�@�\�̃X���b�h�^�C�g���ɂ�郌�X�̏��O�@�\
        # ���荀��: �X���b�h�^�C�g��, ���X���e, �w�背�X�܂ŏ��O(�w�莞�̂�)
        # (���X���̂ݔ�����s��)
        if (!$new_thread_flag && $settings[24] ne '' && $settings[25] ne '') {
            # �X���b�h�^�C�g���ƃ��X���e�̈�v����
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[24]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[25]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref) && defined($res_match_array_ref)) {
                # ��v�����X���b�h�^�C�g���E���X�����o��
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # �w�肵�����X�܂ŏ��O ����
                my @exempt_up_to_res_match;
                if ($settings[26] ne '') {
                    my $exempt_up_to_res_num = int($settings[26]);
                    if ($new_res_no <= $exempt_up_to_res_num) {
                        # ���O�Ώۂ̂��߁A���̂܂ܔz��ɒǉ�
                        @exempt_up_to_res_match = ($exempt_up_to_res_num);
                    } else {
                        # ���XNo���ݒ�l���傫���A���O�ΏۊO���X�̏ꍇ�A
                        # ����擪�ɕt�^���Ĕz��ɒǉ� (���O���莞�ɂ͂��̒l�͏��O����)
                        @exempt_up_to_res_match = ($over_threshold_char . $exempt_up_to_res_num);
                    }
                }

                # ��v���ʔz��ɒǉ�
                push(@{$match_res_exempt_on_res[0]}, @title_match_array);      # ��v�X���b�h�^�C�g��
                push(@{$match_res_exempt_on_res[1]}, @res_match_array);        # ��v���X���e
                push(@{$match_res_exempt_on_res[2]}, @exempt_up_to_res_match); # �w�肵�����X�܂ŏ��O �ݒ�

                # �s�ݒ��v�t���O�𗧂Ă�
                $match_flag ||= 1;
            }
        }

        # �����������݋֎~�@�\(���O)
        # ���荀��: �X���b�h�^�C�g��(��v���擪@ �t��), ���O
        # (�����������݋֎~�@�\�̖��O���̏��O�@�\�̏��O�ݒ�Ɉ�v���Ȃ������ꍇ�̂݁A������s��)
        if ($settings[36] ne '' && $settings[37] ne ''
            && !defined($mu->universal_match([$name], [$self->('EXEMPTING_NAME')], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)))
        {
            # �X���b�h�^�C�g���E���O�̈�v����
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[36], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            my $name_match_array_ref = $mu->universal_match([$name], [$settings[37]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref) && defined($name_match_array_ref)) {
                # ��v�����X���b�h�^�C�g���E���O�����o��
                my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                my @name_match_array = map { ${$_}[0] } @{${$name_match_array_ref}[0]};

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @match_name = (
                    [uniq(@{$match_name[0]}, @title_match_array)], # ��v�X���b�h�^�C�g��
                    [uniq(@{$match_name[1]}, @name_match_array)]   # ��v�������O
                );

                # �s�ݒ��v�t���O�𗧂Ă�
                $match_flag ||= 1;
            }
        }

        # �X���b�h�쐬�}���@�\
        # ���荀��: �X���b�h�^�C�g��, ���X���e
        # (�V�K�X���b�h�쐬���̂ݔ�����s��)
        if ($new_thread_flag && !$threadlog_same_user_found_flag_in_suppress_thread_creation) {
            # �X���쐬�}���i�X���^�C�j�E�X���쐬�}���i���X�j�񔻒�
            if ($settings[10] ne '') {
                # �X���b�h�^�C�g���̈�v����
                my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[10], '', undef(), '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};

                # ���X���e�̈�v���� (�w�肪����ꍇ�̂�)
                my $res_match_array_ref;
                if ($settings[11] ne '') {
                    $res_match_array_ref = $mu->universal_match([$res], [$settings[11]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
                }

                if (defined($title_match_array_ref) && ($settings[11] eq '' || defined($res_match_array_ref))) {
                    # ��v�����X���b�h�^�C�g���E���X�����o��
                    my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                    my @res_match_array = defined($res_match_array_ref) ? map { ${$_}[0] } @{${$res_match_array_ref}[0]} : ();

                    # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                    @match_suppress_thread_creation = (
                        [uniq(@{$match_suppress_thread_creation[0]}, @title_match_array)], # ��v�X���b�h�^�C�g��
                        [uniq(@{$match_suppress_thread_creation[1]}, @res_match_array)]    # ��v���X���e
                    );

                    # �s�ݒ��v�t���O�𗧂Ă�
                    $match_flag ||= 1;
                }
            }

            # �X���쐬�}���i�X���^�C�̂݁j�񔻒�
            if ($settings[9] ne '') {
                # �X���b�h�^�C�g���̈�v����
                my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[9], '', undef(), '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};

                if (defined($title_match_array_ref)) {
                    # ��v�����X���b�h�^�C�g�������o��
                    my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};

                    # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                    @match_suppress_thread_creation = (
                        [uniq(@{$match_suppress_thread_creation[0]}, @title_match_array)], # ��v�X���b�h�^�C�g��
                        [uniq(@{$match_suppress_thread_creation[1]}, '**')]                # ��v���X���e  (�S�Ẵ��X���e�Ɉ�v�̂��߁A**��ǉ�)
                    );

                    # �s�ݒ��v�t���O�𗧂Ă�
                    $match_flag ||= 1;
                }
            }
        }

        # �����������݋֎~�@�\(�X���b�h�^�C�g��)
        # ���荀��: �X���b�h�^�C�g��
        #  (�V�K�X���b�h�쐬���̂ݔ�����s��)
        if ($new_thread_flag && $settings[13] ne '') {
            # �X���b�h�^�C�g���̈�v����
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[13]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref)) {
                # ��v�����X���b�h�^�C�g�������o��
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @match_title = uniq(@match_title, @title_match_array);

                # �s�ݒ��v�t���O�𗧂Ă�
                $match_flag ||= 1;
            }
        }

        # �����������݋֎~�@�\(���X)
        # ���荀��: �X���b�h�^�C�g��(��v���擪@ �t��), ���X���e, ���������O
        if ($settings[15] ne '' && $settings[16] ne '') {
            # �X���b�h�^�C�g���E���X���e�̈�v����
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[15], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[16]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref) && defined($res_match_array_ref)) {
                # ��v�����X���b�h�^�C�g���E���X�����o��
                my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # �Ώۃ��X��o�͗p�ɗא�AND����������������v���X���������o��
                my @res_concat_match_array = map { ${$_}[1] } @{${$res_match_array_ref}[0]};

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @match_res = (
                    [uniq(@{$match_res[0]}, @title_match_array)],       # ��v�X���b�h�^�C�g��
                    [uniq(@{$match_res[1]}, @res_match_array)],         # ��v���X���e
                    [uniq(@{$match_res[2]}, @res_concat_match_array)]   # �Ώۃ��X���e
                );

                # ���������O�w�肪����ꍇ�͐ݒ�l�z��ɒǉ����ă��j�[�N�����s���A�����\�[�g����
                if ($settings[17] ne '') {
                    @valid_exempt_res_length_settings = uniq(@valid_exempt_res_length_settings, int($settings[17]));
                }

                # �s�ݒ��v�t���O�𗧂Ă�
                $match_flag ||= 1;
            }
        }

        # �X���b�h�쐬���̃��X�̋��������������݋֎~�@�\
        # ���荀��: �X���b�h�^�C�g��, ���X���e, �摜�A�b�v
        # (�V�K�X���b�h�쐬���̂ݔ�����s��)
        if ($new_thread_flag && $settings[29] ne '' && $settings[30] ne '') {
            # �X���b�h�^�C�g���ƃ��X���e�̈�v����
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[29], '', undef(), '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[30]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            # �摜�A�b�v���� (�w�肪����ꍇ�̂�)
            my $img_upl;
            if ($settings[31] eq '1' && $upfile_count > 0) {
                $img_upl = 1;
            }

            if (defined($title_match_array_ref) && defined($res_match_array_ref) && ($settings[31] ne '1' || $img_upl)) {
                # ��v�����X���b�h�^�C�g���E���X�����o��
                my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @force_res_match_on_thread_create = (
                    [uniq(@{$force_res_match_on_thread_create[0]}, @title_match_array)], # ��v�X���b�h�^�C�g��
                    [uniq(@{$force_res_match_on_thread_create[1]}, @res_match_array)],   # ��v���X���e
                    $force_res_match_on_thread_create[2] || $img_upl                     # �摜�A�b�v
                );

                # �s�ݒ��v�t���O�𗧂Ă�
                $match_flag ||= 1;
            }
        }

        # �X���b�h�^�C�g���ɂ�郌�X�̋��������������݋֎~�@�\
        # ���荀��: �X���b�h�^�C�g��, ���X���e
        # (���X���̂ݔ�����s��)
        if (!$new_thread_flag && $settings[33] ne '' && $settings[34] ne '') {
            # �X���b�h�^�C�g���ƃ��X���e�̈�v����
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $settings[33], '', undef(), '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            my $res_match_array_ref = $mu->universal_match([$res], [$settings[34]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref) && defined($res_match_array_ref)) {
                # ��v�����X���b�h�^�C�g���E���X�����o��
                my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @force_res_match_on_res = (
                    [uniq(@{$force_res_match_on_res[0]}, @title_match_array)], # ��v�X���b�h�^�C�g��
                    [uniq(@{$force_res_match_on_res[1]}, @res_match_array)]    # ��v���X���e
                );

                # �s�ݒ��v�t���O�𗧂Ă�
                $match_flag ||= 1;
            }
        }

        # �X���b�h�쐬���̃X���^�C�̋��������������݋֎~�@�\
        # ���荀��: �X���b�h�^�C�g��
        # (�V�K�X���b�h�쐬���̂ݔ�����s��)
        if ($new_thread_flag && $settings[28] ne '') {
            # �X���b�h�^�C�g���̈�v����
            my $title_match_array_ref = $mu->universal_match([$title], [$settings[28]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);

            if (defined($title_match_array_ref)) {
                # ��v�����X���b�h�^�C�g�������o��
                my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @force_title_match_on_thread_create = uniq(@force_title_match_on_thread_create, @title_match_array);

                # �s�ݒ��v�t���O�𗧂Ă�
                $match_flag ||= 1;
            }
        }

        # �s�ݒ�̂����ꂩ�Ɉ�v���Ă���ꍇ�̂݁A
        # ��v���[�U�[������v���ʔz��ɒǉ����A���j�[�N�����s��
        if ($match_flag) {
            # ��v���[�U�[�����擾
            my @row_match_host = @{${$validsetting_and_userinfo_matchresult_array_ref}[1]};
            my @row_match_useragent = @{${$validsetting_and_userinfo_matchresult_array_ref}[2]};
            my @row_match_cookiea = @{${$validsetting_and_userinfo_matchresult_array_ref}[3]};
            my @row_match_userid = @{${$validsetting_and_userinfo_matchresult_array_ref}[4]};
            my @row_match_historyid = @{${$validsetting_and_userinfo_matchresult_array_ref}[5]};
            my @row_match_time_range = @{${$validsetting_and_userinfo_matchresult_array_ref}[6]};
            my $row_private_browsing_mode_match_flag = ${$validsetting_and_userinfo_matchresult_array_ref}[7];
            my $match_period_str = ($settings[6] ne '' && $settings[7] ne '' ? $enc_cp932->decode("$settings[6]��$settings[7]") : '');

            # ��v���ʔz��ɒǉ����A���j�[�N�����s��
            @match_host = uniq(@match_host, @row_match_host);
            @match_useragent = uniq(@match_useragent, @row_match_useragent);
            @match_cookiea = uniq(@match_cookiea, @row_match_cookiea);
            @match_userid = uniq(@match_userid, @row_match_userid);
            @match_historyid = uniq(@match_historyid, @row_match_historyid);
            @match_time_range = uniq(@match_time_range, @row_match_time_range);
            @match_period = uniq(@match_period, $match_period_str);

            # �v���C�x�[�g�u���E�W���O���[�h ��v�t���O��K�v�ɉ�����True�ɂ���
            $private_browsing_mode_matched_flag ||= $row_private_browsing_mode_match_flag;
        }
    }

    # �����������݋֎~�@�\(���X) ���������O
    # �ݒ�l�����ŏ��O�ΏۊO�̏ꍇ�A����擪�ɕt�^���Ēǉ� (���O���莞�ɂ͂��̒l�͏��O����)
    my @match_res_length_exempt = map { $_ <= $res_length ? $_ : $under_threshold_char . $_; } @valid_exempt_res_length_settings;

    # init.cgi�Ȃǂɐݒ肪���鎩���������݋֎~�@�\�֘A�̔���
    # ���[�U�[�����擾
    my $time = $self->('TIME');
    my $host = $self->('HOST');
    my $useragent = $self->('USERAGENT');
    my $cookie_a = $self->('COOKIE_A');
    my $user_id = $self->('USER_ID');
    my $history_id = $self->('HISTORY_ID');
    my $is_private_browsing_mode = $self->('IS_PRIVATE_BROWSING_MODE');

    # �w�肵�����XNo�܂ł̎����������݋֎~�@�\
    # ���荀��: ���X�ԍ�, �X���b�h�^�C�g��, ���X1�̏��O�P��, ���X���������O, ���X���e, �z�X�g��UserAgent, CookieA or �o�^ID or ����ID, ���Ԕ͈͎w��
    # (���X���̂ݔ�����s��)
    my @match_up_to_res = (0, [], []);
    my @match_up_to_res_res_length_exempt;
    if (!$new_thread_flag) {
        # �ݒ���o��
        my @up_to_res_number_setting = @{$self->('UP_TO_RES_NUMBER_SETTING_ARRAY_REF')};

        # ���胋�[�v
        foreach my $setting_set_str (@up_to_res_number_setting) {
            # �ݒ�l����
            my @setting_set_array = @{ $mu->number_of_elements_fixed_split($setting_set_str, 10, Matcher::Utils::UTF8_FLAG_FORCE_ON) };
            if (scalar(@setting_set_array) != 10) {
                # �ݒ肪10���ڂł͂Ȃ����̓X�L�b�v
                next;
            }

            # �����P�ꖢ�ݒ莞�X�L�b�v
            if ($setting_set_array[3] eq '') {
                next;
            }

            # ���X�ԍ����͈͊O�̂Ƃ��̓X�L�b�v
            if (int($setting_set_array[0]) < $new_res_no) {
                next;
            }

            # �v���C�x�[�g���[�h����
            my $in_set_private_browsing_mode_match_flg = 0; # �ݒ�Z�b�g���v���C�x�[�g�u���E�W���O���[�h��v�t���O
            if ($setting_set_array[7] eq '1') {
                # �v���C�x�[�g���[�h��ΏۂƂ���ݒ�̏ꍇ�ɁA
                # �v���C�x�[�g���[�h�ł���΃t���O���Z�b�g���A�����łȂ���΃Z�b�g���X�L�b�v
                if ($is_private_browsing_mode) {
                    $in_set_private_browsing_mode_match_flg = 1;
                } else {
                    next;
                }
            }

            # ���X1�̏��O�P�ꔻ��
            if ($setting_set_array[2] ne ''
                && defined($mu->universal_match([$first_res], [$setting_set_array[2]], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
                # ���X1�̏��O�P��ɍ��v�����ꍇ�̓Z�b�g���X�L�b�v
                next;
            }

            # �X���b�h����v����
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $setting_set_array[1], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (!defined($title_match_array_ref)) {
                # �ΏۃX���b�h���ɍ��v���Ȃ��ꍇ(�ے�����ł͍��v�����ꍇ)�ɃZ�b�g���X�L�b�v
                next;
            }

            # ���X���e��v����
            my $res_match_array_ref = $mu->universal_match([$res], [$setting_set_array[3]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (!defined($res_match_array_ref)) {
                # �����P��ƈ�v���Ȃ������ꍇ�̓Z�b�g���X�L�b�v
                next;
            }

            # �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�E���Ԕ͈͎w��̐ݒ蕶����ɂ��āA�u-�v����ɒu������
            foreach my $i (5, 6, 8) {
                $setting_set_array[$i] =~ s/^-$//;
            }

            # �z�X�g��UserAgent�̈�v����
            my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;
            my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[5], ['**', '**'], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (defined($host_useragent_match_array_ref)) {
                $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
            }

            # CookieA or �o�^ID or ����ID�̈�v����
            my @cookiea_userid_historyid_match_array = ([], [], []);
            if ($setting_set_array[6] ne '') {
                my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $setting_set_array[6], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($cookiea_userid_historyid_match_array_ref)) {
                    @cookiea_userid_historyid_match_array = @{$cookiea_userid_historyid_match_array_ref};
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }
            }

            # �u�z�X�g��UserAgent�v���uCookieA or �o�^ID or ����ID�v��
            # �ǂ��炩�ň�v���Ă��Ȃ��Ƃ��́A�Z�b�g���X�L�b�v
            if ($host_useragent_or_cookiea_userid_historyid_matched_flg == 0) {
                next;
            }

            # ���Ԕ͈͎w��̈�v����
            my @time_range_match_array;
            if ($setting_set_array[8] ne '') {
                if ($mu->is_in_time_range($setting_set_array[8])) {
                    @time_range_match_array = ($setting_set_array[7]);
                } else {
                    # ���Ԕ͈͎w�肪����A���v���Ȃ��Ƃ��̓Z�b�g���X�L�b�v
                    next;
                }
            }

            # ��v�����X���b�h���E���X�����o��
            my @title_match_array = map { ${$_}[0] } @{$title_match_array_ref};
            my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

            # ��v���ʔz��ɒǉ����āA���j�[�N������
            @match_up_to_res = (
                $match_up_to_res[0] + 1,                            # ��v���J�E���^�[
                [uniq(@{$match_up_to_res[1]}, @title_match_array)], # ��v�X���b�h�^�C�g��
                [uniq(@{$match_up_to_res[2]}, @res_match_array)]    # ��v���X���e
            );
            @match_host = uniq(@match_host, @{${$host_useragent_match_array_ref}[0]}); # ��v�z�X�g
            @match_useragent = uniq(@match_useragent, @{${$host_useragent_match_array_ref}[1]}); # ��vUserAgent
            @match_cookiea = uniq(@match_cookiea, @{$cookiea_userid_historyid_match_array[0]}); # ��vCookieA
            @match_userid = uniq(@match_userid, @{$cookiea_userid_historyid_match_array[1]}); # ��v�o�^ID
            @match_historyid = uniq(@match_historyid, @{$cookiea_userid_historyid_match_array[2]}); # ��v����ID
            @match_time_range = uniq(@match_time_range, @time_range_match_array); # ��v���Ԕ͈�

            # ���X���������O
            if ($setting_set_array[4] ne '') {
                my $exempt_res_length = int($setting_set_array[4]);
                if ($exempt_res_length <= $res_length) {
                    @match_up_to_res_res_length_exempt = uniq(@match_up_to_res_res_length_exempt, $exempt_res_length);
                } else {
                    # �ݒ�l�����ŏ��O�ΏۊO�̏ꍇ�A����擪�ɕt�^���Ēǉ� (���O���莞�ɂ͂��̒l�͏��O����)
                    @match_up_to_res_res_length_exempt = uniq(@match_up_to_res_res_length_exempt, $under_threshold_char . $exempt_res_length);
                }
            }

            # �v���C�x�[�g�u���E�W���O���[�h ��v�t���O��K�v�ɉ�����True�ɂ���
            $private_browsing_mode_matched_flag ||= $in_set_private_browsing_mode_match_flg;
        }
    }

    # �X���b�hNo/�X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\�̈�v�t���O
    my $thread_num_or_name_target_prohibit_flag;

    # �X���b�hNo�������������݋֎~�@�\�̃��X���������œ��삷��@�\
    # ���荀��: ���X���e
    # (�u�����������݋֎~�@�\(���X)�v�Ɠ����o�͌��ʂƂȂ�)
    my @thread_number_res_target = @{$self->('THREAD_NUMBER_RES_TARGET_ARRAY_REF')};
    if (scalar(@thread_number_res_target) > 0) {
        # ��v����
        my @thread_number_res_target_hold_hours = @{$self->('THREAD_NUMBER_RES_TARGET_HOLD_HOURS_ARRAY_REF')};
        foreach my $target_hash_ref (@thread_number_res_target) {
            # �n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
            if (ref($target_hash_ref) ne 'HASH') {
                next;
            }
            my %target_hash = %{$target_hash_ref};

            # �K�{�L�[�������A�������́A�ݒ莞�Ԃ��o�߂����ݒ�̓X�L�b�v
            if (!exists($target_hash{thread_number})
                || !exists($target_hash{time})
                || !exists($target_hash{type}) || $target_hash{type} < 0 || $target_hash{type} > 6
                || ($target_hash{type} >= 1
                    && ($target_hash{time} + $thread_number_res_target_hold_hours[$target_hash{type}] * 3600) < $time
                )
            ) {
                next;
            }

            # ���X���e�̈�v����
            if (!defined($mu->universal_match(([$res], ["no=$target_hash{thread_number}"], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)))) {
                next;
            }

            # ���ʏo�͗p�ɐ��`���āA��v���ʔz��ɒǉ�
            # (��v���ʂƂ��ďo�͂�����e�͌Œ�̂��߁A�z��Ƃ��ė\�ߗp�ӂ���)
            my @title_match_array = ('@ **');
            my @res_match_array = ("no=$target_hash{thread_number}");
            my @res_concat_match_array = ("no=$target_hash{thread_number}");
            my @host_match_array = ('**');
            my @useragent_match_array = ('**');

            # ��v���ʔz��ɒǉ����A���j�[�N�����s��
            @match_res = (
                [uniq(@{$match_res[0]}, @title_match_array)],      # ��v�X���b�h�^�C�g��
                [uniq(@{$match_res[1]}, @res_match_array)],        # ��v���X���e
                [uniq(@{$match_res[2]}, @res_concat_match_array)]  # �Ώۃ��X���e
            );
            @match_host = uniq(@match_host, @host_match_array);
            @match_useragent = uniq(@match_useragent, @useragent_match_array);

            # �t���O�𗧂Ă�
            $thread_num_or_name_target_prohibit_flag ||= 1;
        }
    }

    # �X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\
    # ���荀��: �X���b�h�^�C�g��, ���X���e
    # (�u�����������݋֎~�@�\(���X)�v�Ɠ����o�͌��ʂƂȂ�)
    my @thread_title_res_target = @{$self->('THREAD_TITLE_RES_TARGET_ARRAY_REF')};
    if (scalar(@thread_title_res_target) > 0) {
        # �����P������������ɕϊ�
        # (�ŏ��̗v�f�́A���index���g�p���ď������邽�߂̃_�~�[�v�f�Ƃ���)
        my @decoded_restrict_keyword_array = (
            undef,
            map { $enc_cp932->decode($_) } @{$self->('THREAD_TITLE_RES_TARGET_RESTRICT_KEYWORD_ARRAY_REF')}
        );

        # �������O�P������������ɕϊ�
        # (�ŏ��̗v�f�́A���index���g�p���ď������邽�߂̃_�~�[�v�f�Ƃ���)
        my @decoded_restrict_exempt_keyword_array = (
            undef,
            map { $enc_cp932->decode($_) } @{$self->('THREAD_TITLE_RES_TARGET_RESTRICT_EXEMPT_KEYWORD_ARRAY_REF')}
        );

        # �������Ԕz����擾
        # (�ŏ��̗v�f�́A���index���g�p���ď������邽�߂̃_�~�[�v�f�Ƃ���)
        my @target_hold_hour = (undef, @{$self->('THREAD_TITLE_RES_TARGET_RESTRICT_HOLD_HOUR_ARRAY_REF')});

        # �����ݒ�n�b�V�����琧���Ώۂ��ǂ������肷��
        foreach my $target_hash_ref (@thread_title_res_target) {
            # �n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
            if (ref($target_hash_ref) ne 'HASH') {
                next;
            }
            my %target_hash = %{$target_hash_ref};

            # word_type���L�^����Ă��Ȃ��ꍇ�́A�����P��1�Ƃ݂Ȃ�
            if (!exists($target_hash{word_type})) {
                $target_hash{word_type} = 1;
            }

            # �ُ�ݒ�l�A�������́A�ݒ莞�Ԃ��o�߂����ݒ�̓X�L�b�v
            if (!exists($target_hash{thread_title})
                || !exists($target_hash{type}) || $target_hash{type} < 0 || $target_hash{type} > 6
                || !exists($target_hash{time}) || !defined($target_hash{time})
                || !exists($target_hash{word_type}) || $target_hash{word_type} < 1 || $target_hash{word_type} > 20
                || ($target_hash{type} != 0 && ($target_hash{time} + $target_hold_hour[$target_hash{type}] * 3600) < $time)
            ) {
                next;
            }

            # �X���b�h�^�C�g���̈�v����E��v�X���b�h�^�C�g���̎��o��
            my $title_match_array_ref = $mu->universal_match([$title], [$target_hash{thread_title}], ['@ '], ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (!defined($title_match_array_ref)) {
                next;
            }
            my @title_match_array = map { ${$_}[0] } @{${$title_match_array_ref}[0]};

            # ���X���e�̒ʏ��v����
            my $decoded_restrict_keyword = $decoded_restrict_keyword_array[$target_hash{word_type}]; # word_type����v������s�������P�������
            my $res_match_array_ref = $mu->universal_match([$res], [$decoded_restrict_keyword], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (defined($res_match_array_ref)) {
                # ��v���X�ƁA�Ώۃ��X��o�͗p�ɗא�AND����������������v���X���������o��
                my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};
                my @res_concat_match_array = map { ${$_}[1] } @{${$res_match_array_ref}[0]};

                # ��v���ʂƂ��ďo�͂���ꕔ�̍��ڂ̓��e�͌Œ�̂��߁A�z���\�ߗp�ӂ���
                my @host_match_array = ('**');
                my @useragent_match_array = ('**');

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @match_res = (
                    [uniq(@{$match_res[0]}, @title_match_array)],      # ��v�X���b�h�^�C�g��
                    [uniq(@{$match_res[1]}, @res_match_array)],        # ��v���X���e
                    [uniq(@{$match_res[2]}, @res_concat_match_array)]  # �Ώۃ��X���e
                );
                @match_host = uniq(@match_host, @host_match_array);
                @match_useragent = uniq(@match_useragent, @useragent_match_array);

                # �t���O�𗧂Ă�
                $thread_num_or_name_target_prohibit_flag ||= 1;
            }

            # ���X���e�̏��O��v����
            my $decoded_restrict_exempt_keyword = $decoded_restrict_exempt_keyword_array[$target_hash{word_type}]; # word_type����v������s�����O�P�������
            my $exempt_res_match_array_ref = $mu->universal_match([$res], [$decoded_restrict_exempt_keyword], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (defined($exempt_res_match_array_ref)) {
                # ���X���e�����O��v���Ă��鎞�́A
                # �����������݋֎~�@�\�̃X���b�h�^�C�g���ɂ�郌�X�̏��O�@�\�̈�v�Ƃ��ď���

                # ���O��v���X�����o��
                my @exempt_res_match_array = map { ${$_}[0] } @{${$exempt_res_match_array_ref}[0]};

                # �����������݋֎~�@�\�̃X���b�h�^�C�g���ɂ�郌�X�̏��O�@�\��
                # ��v���ʔz��ɒǉ�
                push(@{$match_res_exempt_on_res[0]}, @title_match_array);      # ��v�X���b�h�^�C�g��
                push(@{$match_res_exempt_on_res[1]}, @exempt_res_match_array); # ��v���X���e
            }
        }
    }

    # �����񓊍e���̎����������݋֎~�@�\
    # (���X���̂ݔ�����s��)
    my $multiple_submissions_redirect_flag;
    my @match_multiple_submissions = ();
    if (!$new_thread_flag) {
        # ���[�U�[�J�E���g���O�ǉ�����
        # ���荀��: �X���b�h�^�C�g��, ���X1�̏��O�P��, ���X���e, �z�X�g��UserAgent, CookieA or �o�^ID or ����ID, �v���C�x�[�g���[�h, ���Ԕ͈͎w��
        my @multiple_submissions_setting = @{$self->('MULTIPLE_SUBMISSIONS_SETTING_ARRAY_REF')};
        foreach my $setting_str (@multiple_submissions_setting) {
            # �ݒ�l����
            my @setting_set_array = @{ $mu->number_of_elements_fixed_split($setting_str, 9, Matcher::Utils::UTF8_FLAG_FORCE_ON) };
            if (scalar(@setting_set_array) != 9
                || $setting_set_array[0] eq $disable_setting_char
                || $setting_set_array[1] eq ''
                || $setting_set_array[3] eq ''
            ) {
                # �ݒ肪9���ڂł͂Ȃ��A������Ɂ��A�X���b�h�^�C�g�� or �����P�ꂪ���ݒ莞�̓Z�b�g���X�L�b�v
                next;
            }

            # �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�E�v���C�x�[�g���[�h�E���Ԕ͈͎w��ɂ��āA
            # �u-�v���󕶎���ɒu��������
            foreach my $i (4 .. 7) {
                $setting_set_array[$i] =~ s/^-$//;
            }

            # �v���C�x�[�g���[�h����
            my $in_set_private_browsing_mode_match_flg = 0; # �ݒ�Z�b�g���v���C�x�[�g�u���E�W���O���[�h��v�t���O
            if ($setting_set_array[6] eq '1') {
                # �v���C�x�[�g���[�h��ΏۂƂ���ݒ�̏ꍇ�ɁA
                # �v���C�x�[�g���[�h�ł���΃t���O���Z�b�g���A�����łȂ���΃Z�b�g���X�L�b�v
                if ($is_private_browsing_mode) {
                    $in_set_private_browsing_mode_match_flg = 1;
                } else {
                    next;
                }
            }

            # ���X1�̏��O�P�ꔻ��
            if ($setting_set_array[2] ne ''
                && defined($mu->universal_match([$first_res], [$setting_set_array[2]], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
                # ���X1�̏��O�P��ɍ��v�����ꍇ�̓Z�b�g���X�L�b�v
                next;
            }

            # �X���b�h����v����
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $setting_set_array[1], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (!defined($title_match_array_ref)) {
                # �ΏۃX���b�h���ɍ��v���Ȃ��ꍇ(�ے�����ł͍��v�����ꍇ)�ɃZ�b�g���X�L�b�v
                next;
            }

            # ���X���e��v����
            my $res_match_array_ref = $mu->universal_match([$res], [$setting_set_array[3]], undef(), ['**'], Matcher::Utils::UTF8_FLAG_FORCE_ON);
            if (!defined($res_match_array_ref)) {
                # �����P��ƈ�v���Ȃ������ꍇ�̓Z�b�g���X�L�b�v
                next;
            }

            # �u�z�X�g��UserAgent�v���uCookieA or �o�^ID or ����ID�v�̂����ꂩ�ň�v�������ǂ����̃t���O
            my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;

            # �z�X�g��UserAgent�̈�v����
            my @host_useragent_match_array = ([], []);
            if ($setting_set_array[4] ne '') {
                my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[4], ['**', '**'], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($host_useragent_match_array_ref)) {
                    @host_useragent_match_array = @{$host_useragent_match_array_ref};
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }
            }

            # CookieA or �o�^ID or ����ID�̈�v����
            my @cookiea_userid_historyid_match_array = ([], [], []);
            if ($setting_set_array[5] ne '') {
                my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $setting_set_array[5], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
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
            if ($setting_set_array[7] ne '') {
                if ($mu->is_in_time_range($setting_set_array[7])) {
                    @match_time_range_array = ($setting_set_array[7]);
                } else {
                    next;
                }
            }

            # ��v�������X�����o��
            my @res_match_array = map { ${$_}[0] } @{${$res_match_array_ref}[0]};

            # ��v���ʔz��ɒǉ����āA���j�[�N������
            @match_multiple_submissions = uniq(@match_multiple_submissions, @res_match_array); # ��v���X
            @match_host = uniq(@match_host, @{$host_useragent_match_array[0]}); # ��v�z�X�g
            @match_useragent = uniq(@match_useragent, @{$host_useragent_match_array[1]}); # ��vUserAgent
            @match_cookiea = uniq(@match_cookiea, @{$cookiea_userid_historyid_match_array[0]}); # ��vCookieA
            @match_userid = uniq(@match_userid, @{$cookiea_userid_historyid_match_array[1]}); # ��v�o�^ID
            @match_historyid = uniq(@match_historyid, @{$cookiea_userid_historyid_match_array[2]}); # ��v����ID
            @match_time_range = uniq(@match_time_range, @match_time_range_array); # ��v���Ԕ͈�

            # �v���C�x�[�g�u���E�W���O���[�h ��v�t���O��K�v�ɉ�����True�ɂ���
            $private_browsing_mode_matched_flag ||= $in_set_private_browsing_mode_match_flg;
        }

        # ���_�C���N�g����ƁA���݃��[�U�[���̃��[�U�[�J�E���g���O�z��ւ̒ǉ�
        # (���[�U�[�J�E���g���O�ǉ��Ώۂ̏ꍇ�̂�)
        if (scalar(@match_multiple_submissions) > 0) {
            # ���[�U�[�J�E���g���O�z�񃊃t�@�����X���擾
            my $multiple_submissions_validlog_array_ref = $self->('MULTIPLE_SUBMISSIONS_VALIDLOG_ARRAY_REF');

            # ���ꃆ�[�U�[�̓��e���ɂ�郊�_�C���N�g����
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

            # ���[�U�[�J�E���g���O�z��Ɍ��݃��[�U�[����ǉ�
            if ($self->('MULTIPLE_SUBMISSIONS_LOG_RECORD_HOST_FLAG')) {
                push(@{$multiple_submissions_validlog_array_ref}, [$host, $cookie_a, $user_id, $history_id, $time]);
            } else {
                push(@{$multiple_submissions_validlog_array_ref}, ['', $cookie_a, $user_id, $history_id, $time]);
            }
        }
    }

    # �ÃX��age�̎����������݋֎~�@�\
    # (age�̃��X���̂ݔ�����s��)
    my $old_thread_age_redirect_flag;
    my $match_old_thread_age_flag;
    if (!$new_thread_flag && $age_flag) {
        # ���O���X�̃^�C���X�^���v�����o��
        my $last_res_timestamp = ${${$log_array_ref}[$#{$log_array_ref}]}[11];

        # �ÃX��age���[�U�[�J�E���g���O�ǉ�����
        # ���荀��: �X���b�h�^�C�g��, ���O���X�������ԑO, �z�X�g��UserAgent, CookieA or �o�^ID or ����ID, �v���C�x�[�g���[�h, ���Ԕ͈͎w��
        my @old_thread_age_setting = @{$self->('OLD_THREAD_AGE_SETTING_ARRAY_REF')};
        foreach my $setting_str (@old_thread_age_setting) {
            # �ݒ�l����
            my @setting_set_array = @{ $mu->number_of_elements_fixed_split($setting_str, 8, Matcher::Utils::UTF8_FLAG_FORCE_ON) };
            if (scalar(@setting_set_array) != 8
                || $setting_set_array[0] eq $disable_setting_char
                || $setting_set_array[1] eq ''
                || $setting_set_array[2] eq ''
            ) {
                # �ݒ肪8���ڂł͂Ȃ��A������Ɂ��A�X���b�h�^�C�g���E���O���X�������ԑO�����ݒ莞�̓Z�b�g���X�L�b�v
                next;
            }

            # �z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�E�v���C�x�[�g���[�h�E���Ԕ͈͎w��ɂ��āA
            # �u-�v���󕶎���ɒu��������
            foreach my $i (3 .. 6) {
                $setting_set_array[$i] =~ s/^-$//;
            }

            # �v���C�x�[�g���[�h����
            my $in_set_private_browsing_mode_match_flg = 0; # �ݒ�Z�b�g���v���C�x�[�g�u���E�W���O���[�h��v�t���O
            if ($setting_set_array[5] eq '1') {
                # �v���C�x�[�g���[�h��ΏۂƂ���ݒ�̏ꍇ�ɁA
                # �v���C�x�[�g���[�h�ł���΃t���O���Z�b�g���A�����łȂ���΃Z�b�g���X�L�b�v
                if ($is_private_browsing_mode) {
                    $in_set_private_browsing_mode_match_flg = 1;
                } else {
                    next;
                }
            }

            # �u���O���X�������ԑO�v����
            if (($time - $setting_set_array[2] * 3600) < $last_res_timestamp) {
                # �u���O���X�������ԑO�v�ɒB���Ă��Ȃ��ꍇ�̓Z�b�g���X�L�b�v
                next;
            }

            # �X���b�h����v����
            my ($title_match_array_ref) = @{$mu->get_matched_thread_title_to_setting_and_whether_its_not_match($title, $setting_set_array[1], '', '@ ', '**', Matcher::Utils::UTF8_FLAG_FORCE_ON)};
            if (!defined($title_match_array_ref)) {
                # �ΏۃX���b�h���ɍ��v���Ȃ��ꍇ(�ے�����ł͍��v�����ꍇ)�ɃZ�b�g���X�L�b�v
                next;
            }

            # �u�z�X�g��UserAgent�v���uCookieA or �o�^ID or ����ID�v�̂����ꂩ�ň�v�������ǂ����̃t���O
            my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;

            # �z�X�g��UserAgent�̈�v����
            my @host_useragent_match_array = ([], []);
            if ($setting_set_array[3] ne '') {
                my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[3], ['**', '**'], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($host_useragent_match_array_ref)) {
                    @host_useragent_match_array = @{$host_useragent_match_array_ref};
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }
            }

            # CookieA or �o�^ID or ����ID�̈�v����
            my @cookiea_userid_historyid_match_array = ([], [], []);
            if ($setting_set_array[4] ne '') {
                my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $setting_set_array[4], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
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
            if ($setting_set_array[6] ne '') {
                if ($mu->is_in_time_range($setting_set_array[6])) {
                    @match_time_range_array = ($setting_set_array[6]);
                } else {
                    next;
                }
            }

            # ��v�t���O�𗧂Ă�
            $match_old_thread_age_flag ||= 1;

            # ��v���ʔz��ɒǉ����āA���j�[�N������
            @match_host = uniq(@match_host, @{$host_useragent_match_array[0]}); # ��v�z�X�g
            @match_useragent = uniq(@match_useragent, @{$host_useragent_match_array[1]}); # ��vUserAgent
            @match_cookiea = uniq(@match_cookiea, @{$cookiea_userid_historyid_match_array[0]}); # ��vCookieA
            @match_userid = uniq(@match_userid, @{$cookiea_userid_historyid_match_array[1]}); # ��v�o�^ID
            @match_historyid = uniq(@match_historyid, @{$cookiea_userid_historyid_match_array[2]}); # ��v����ID
            @match_time_range = uniq(@match_time_range, @match_time_range_array); # ��v���Ԕ͈�

            # �v���C�x�[�g�u���E�W���O���[�h ��v�t���O��K�v�ɉ�����True�ɂ���
            $private_browsing_mode_matched_flag ||= $in_set_private_browsing_mode_match_flg;
        }

        # ���_�C���N�g����ƁA���݃��[�U�[���̌ÃX��age���[�U�[�J�E���g���O�z��ւ̒ǉ�
        # (�ÃX��age���[�U�[�J�E���g���O�ǉ��Ώۂ̏ꍇ�̂�)
        if ($match_old_thread_age_flag) {
            # �ÃX��age���[�U�[�J�E���g���O�z�񃊃t�@�����X���擾
            my $old_thread_age_validlog_array_ref = $self->('OLD_THREAD_AGE_VALIDLOG_ARRAY_REF');

            # ���ꃆ�[�U�[�̓��e���ɂ�郊�_�C���N�g����
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

            # �ÃX��age���[�U�[�J�E���g���O�z��Ɍ��݃��[�U�[����ǉ�
            if ($self->('OLD_THREAD_AGE_LOG_RECORD_HOST_FLAG')) {
                push(@{$old_thread_age_validlog_array_ref}, [$host, $cookie_a, $user_id, $history_id, $time]);
            } else {
                push(@{$old_thread_age_validlog_array_ref}, ['', $cookie_a, $user_id, $history_id, $time]);
            }
        }
    }

    # �摜�̎����������݋֎~�@�\
    # ���荀��: �X���b�h�^�C�g��, �ϊ��O/�ϊ���摜��MD5, ��v�����O�o�̓R�����g, �z�X�g��UserAgent, CookieA or �o�^ID or ����ID
    my @match_img_md5 = ([], [], []);
    my @combination_img_md5 = @{$self->('COMBINATION_IMG_MD5_ARRAY_REF')};
    if (scalar(@combination_img_md5) > 0) {
        my @image_md5_concat_one_dimensional_array = map { (grep { $_ ne '' } @{$_}) } @{$image_md5_array_ref_array_ref};
        if (scalar(@image_md5_concat_one_dimensional_array) > 0) {
            foreach my $setting_set_str (@combination_img_md5) {
                # ��v������{
                my @setting_set_array = split(/:/, $enc_cp932->decode($setting_set_str), 5);
                if (scalar(@setting_set_array) != 5) {
                    next;
                }

                # �X���b�h�^�C�g���E�z�X�g��UserAgent�ECookieA or �o�^ID or ����ID�̐ݒ蕶����ɂ��āA�u-�v����ɒu������
                foreach my $i (0, 3, 4) {
                    $setting_set_array[$i] =~ s/^-$//;
                }

                # MD5�̈�v����
                my @setting_md5_array = grep { $_ ne '' } split(/,/, $setting_set_array[1]);
                my @md5_match_array = grep {
                    my $setting_md5 = $_;
                    grep { $_ eq $setting_md5 } @image_md5_concat_one_dimensional_array;
                } @setting_md5_array;
                if (scalar(@md5_match_array) == 0) {
                    next;
                }

                # �X���b�h�^�C�g���̔ے��v����
                my @title_not_match_settings_array;
                if ($setting_set_array[0] ne '') {
                    if (defined($mu->universal_match([$title], [$setting_set_array[0]], undef(), undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON))) {
                        # �ے�����̂��߁A��v���Ă��܂����ꍇ�̓X�L�b�v
                        next;
                    }
                    # ��v���Ȃ������ꍇ�́A�ݒ�l��ۊ�
                    push(@title_not_match_settings_array, $setting_set_array[0]);
                }

                # �z�X�g��UserAgent�̈�v����
                my $host_useragent_or_cookiea_userid_historyid_matched_flg = 0;
                my ($host_useragent_match_array_ref) = @{$mu->get_matched_host_useragent_and_whether_its_not_match($host, $useragent, $setting_set_array[3], undef(), Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                if (defined($host_useragent_match_array_ref)) {
                    $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                }

                # CookieA or �o�^ID or ����ID�̈�v����
                my @cookiea_userid_historyid_match_array = ([], [], []);
                if ($setting_set_array[4] ne '') {
                    my ($cookiea_userid_historyid_match_array_ref) = @{$mu->get_matched_cookiea_userid_historyid_and_whether_its_not_match($cookie_a, $user_id, $history_id, $setting_set_array[4], Matcher::Utils::UTF8_FLAG_FORCE_ON)};
                    if (defined($cookiea_userid_historyid_match_array_ref)) {
                        @cookiea_userid_historyid_match_array = @{$cookiea_userid_historyid_match_array_ref};
                        $host_useragent_or_cookiea_userid_historyid_matched_flg = 1;
                    }
                }

                if ($host_useragent_or_cookiea_userid_historyid_matched_flg == 0) {
                    # �u�z�X�g��UserAgent�v���uCookieA or �o�^ID or ����ID�v��
                    # �ǂ��炩�ň�v���Ă��Ȃ��Ƃ��́A�X�L�b�v
                    next;
                }

                # ��v���ʔz��ɒǉ����A���j�[�N�����s��
                @match_img_md5 = (
                    [uniq(@{$match_img_md5[0]}, @title_not_match_settings_array)], # �X���b�h�^�C�g���ے����
                    [uniq(@{$match_img_md5[1]}, @md5_match_array)],                # ��v�摜MD5
                    [uniq(@{$match_img_md5[3]}, $setting_set_array[2])]            # ��v�����O�o�̓R�����g
                );
            }
        }
    }

    # ���X���ɁA
    # �����������݋֎~�@�\(���O�E���X)�A�w�肵�����XNo�܂ł̎����������݋֎~�@�\�A���������������݋֎~�@�\�ȊO��
    # �����������݋֎~�@�\�Ɉ�v�������ǂ���
    my $other_res_match_on_res_flag =
        !$new_thread_flag
        && ($multiple_submissions_redirect_flag || $old_thread_age_redirect_flag);

    # �X���b�h�쐬�}���@�\�E�����������݋֎~�@�\�̃X���b�h�쐬���̃��X�̏��O�@�\
    # ��������
    # �����������݋֎~�@�\�̃X���b�h�^�C�g���ɂ�郌�X�̏��O�@�\(������������v���J�E���g)��
    # �ݒ�l�Ɉ�v�������ǂ���
    my $res_exempt_match_flag =
        scalar(@{$match_res_exempt_on_thread_create[0]}) > 0
        || scalar(@{$match_res_exempt_on_res[0]}) - scalar(grep { index($_, $over_threshold_char) >= 0 } @{$match_res_exempt_on_res[2]}) > 0;

    # �X���b�h�쐬�}���@�\�E�����������݋֎~�@�\(���ɃX���b�h�^�C�g������)�̏��O�@�\��
    # �ݒ�l�Ɉ�v�������ǂ���
    my $title_exempt_match_flag = scalar(@match_title_exempt_on_thread_create) > 0;

    # �����������݋֎~�@�\(���X) ���������O�̐ݒ�l�Ɉ�v�������ǂ���
    # (���͏��O�ΏۊO�̂��߁A�������������v�����J�E���g����)
    my $res_length_exempt_match_flag = scalar(grep { index($_, $under_threshold_char) == -1 } @match_res_length_exempt) > 0;

    # �w�肵�����XNo�܂ł̎����������݋֎~�@�\ ���������O�̐ݒ�l�Ɉ�v�������ǂ���
    # (���͏��O�ΏۊO�̂��߁A�������������v�����J�E���g����)
    my $up_to_res_res_length_exempt_match_flag = scalar(grep { index($_, $under_threshold_char) == -1 } @match_up_to_res_res_length_exempt) > 0;

    # �X���b�h�쐬�}���@�\�E�����������݋֎~�@�\(���ɃX���b�h�^�C�g������)�̏��O�@�\��
    # ���O�Ώۂ��ǂ���
    my $title_prohibit_exempt_flag =
        scalar(@{$match_name[0]}) == 0
            && (scalar(@{$match_suppress_thread_creation[0]}) > 0 || scalar(@match_title) > 0)
            && $title_exempt_match_flag;

    # �X���b�h�쐬�}���@�\�E�����������݋֎~�@�\�̃X���b�h�쐬���̃��X�̏��O�@�\��
    # ���O�Ώۂ��ǂ���
    my $res_prohibit_exempt_flag =
        scalar(@{$match_name[0]}) == 0
            && (!$title_prohibit_exempt_flag
                || (scalar(@{$match_res[0]}) > 0 && !$res_length_exempt_match_flag)
                || ($match_up_to_res[0] > 0 && !$up_to_res_res_length_exempt_match_flag)
                || $other_res_match_on_res_flag
            )
            && $res_exempt_match_flag;

    # �����������݋֎~�@�\(���X)�̕��������O�ɍ��v���Ă������ǂ���
    my $res_length_prohibit_exempt_flag =
        scalar(@{$match_name[0]}) == 0
            && scalar(@{$match_suppress_thread_creation[0]}) == 0
            && (scalar(@match_title) == 0 || $title_exempt_match_flag)
            && scalar(@{$match_res[0]}) > 0
            && $res_length_exempt_match_flag;

    # �w�肵�����XNo�܂ł̎����������݋֎~�@�\�̕��������O�ɍ��v���Ă������ǂ���
    my $up_to_res_res_length_prohibit_exempt_flag =
        scalar(@{$match_name[0]}) == 0
            && $match_up_to_res[0] > 0
            && $up_to_res_res_length_exempt_match_flag;

    # ���������������݋֎~�@�\�ō��v�������ǂ���
    my $force_match_flag =
        scalar(@{$force_res_match_on_thread_create[0]}) > 0
            || scalar(@{$force_res_match_on_res[0]}) > 0
            || scalar(@force_title_match_on_thread_create) > 0;

    # �摜�̎����������݋֎~�@�\�ō��v�������ǂ���
    my $img_md5_match_flag = scalar(@{$match_img_md5[1]}) > 0;

    # ���O�Ɋ܂܂�郆�[�U�[���ǂ���
    my $log_exist_user_flag =
        $self->('LOG_EXIST_HOST_FLAG')
            || $self->('LOG_EXIST_COOKIEA_FLAG')
            || $self->('LOG_EXIST_USERID_FLAG')
            || $self->('LOG_EXIST_HISTORYID_FLAG');

    # ���O�Ɋ܂܂��݂̂̃��[�U�[���ǂ���
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

    # �X���b�h�쐬�}���@�\�̑Ώۂł��邩�ǂ���
    my $suppress_thread_creation_flag =
        $new_thread_flag
            && scalar(@{$match_name[0]}) == 0
            && scalar(@{$match_suppress_thread_creation[0]}) > 0
            && !$res_exempt_match_flag
            && !$title_exempt_match_flag
            && !$force_match_flag
            && !$img_md5_match_flag;

    # ���_�C���N�g�̑Ώۂł��邩�ǂ���
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

    # �������݋֎~���O�ǋL�Ώۂł��邩�ǂ���
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

    # �����񓊍e���̎����������݋֎~�@�\ ���[�U�[�J�E���g���O�ǋL�Ώۂł��邩�ǂ���
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

    # �ÃX��age�̎����������݋֎~�@�\ �ÃX��age���[�U�[�J�E���g���O�ǋL�Ώۂł��邩�ǂ���
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

    # �������݋֎~���O�ǋL�Ώۂł���΁A�ǋL���e���쐬
    my $log_add_contents;
    if ($log_add_flag) {
        # Cookie A�������s�̏ꍇ�ɔ��s����
        if (!defined($cookie_a)) {
            my UniqueCookie $cookie_a_instance = $self->('COOKIE_A_INSTANCE');
            $cookie_a = $cookie_a_instance->value(1);
            $self->('COOKIE_A', $cookie_a);
        }

        # ���O�Ɋ܂܂��݂̂̃��[�U�[�̏ꍇ�́A�ꕔ�̏o�͍��ڂŁu-----�v���o��
        my $log_only = $log_exist_only_user_flag ? '-----' : '';

        # �X���b�h�쐬�}���Ώۂ̏ꍇ�́A�ꕔ�̏o�͍��ڂŐ擪�Ɂu���v��t������
        my $thread_create_suppress_str = $suppress_thread_creation_flag ? '��' : '';

        # �������ݓ��e�ƈ�v�����֎~�Ώە�����Ȃǂ����O�o�͍��ڂɒǉ�
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
        my $add_old_thread_age = $log_only || ($old_thread_age_redirect_flag ? '��' : '');
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

        # ���O,�X���b�h�^�C�g��,���X���e�̔��p�J���}����菜��
        $add_name =~ tr/,//d;
        $add_title =~ tr/,//d;
        $add_res =~ tr/,//d;

        # �X�e�[�^�X��
        my $status;
        if ($log_exist_only_user_flag) {
            # ���O�Ɋ܂܂��݂̂̃��[�U�[�̏ꍇ�́u-�v���o��
            $status = '-';
        } elsif ($new_thread_flag) {
            $status = $thread_create_suppress_str . '�쐬';
        } else {
            $status = '��';
        }
        if ($thread_num_or_name_target_prohibit_flag) {
            # �X���b�hNo/�X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\��
            # ��v�����ꍇ�ɁA�X�e�[�^�X�񖖔��Ɂu���v���o�͂���
            $status .= '��';
        }

        # ���t��
        my $date = $self->('DATE');

        # CookieA���s��
        my $cookie_a_issuing_str = '';
        if ($self->('COOKIE_A_ISSUING_FLAG')) {
            $cookie_a_issuing_str = '����';
        }

        # �X���^�C���O��
        my $title_exempt = '';
        if ($title_prohibit_exempt_flag) {
            $title_exempt = '���O';
        }

        # ���O��
        my $exempt = '';
        if ((!$other_res_match_on_res_flag
                && (($res_length_prohibit_exempt_flag && $up_to_res_res_length_prohibit_exempt_flag)
                    || ($res_length_prohibit_exempt_flag && $match_up_to_res[0] == 0)
                    || ($up_to_res_res_length_prohibit_exempt_flag && scalar(@{$match_res[0]}) == 0)
                )
            )
            || $res_prohibit_exempt_flag
        ) {
            $exempt = '���O';
        }

        # ������
        my $force_prohibit = '';
        if ($force_match_flag) {
            $force_prohibit .= '��1';
        }
        if ($img_md5_match_flag) {
            $force_prohibit .= '��p';
        }

        # URL�� (���X�����A���O�ɂ��X���b�h�쐬���̂݁A@auto_post_prohibit_log_concat_url�ƃX���b�hNo���������ďo��)
        my $url = '';
        if (!$new_thread_flag
            || (!$suppress_thread_creation_flag && !$redirect_flag && ($title_exempt ne '' || $exempt ne ''))
        ) {
            $url = $self->('LOG_CONCAT_URL') . $thread_no;
        }

        # �v���C�x�[�g���[�h/�v���C�x�[�g���[�h�����
        my $private_browsing_mode_str = $is_private_browsing_mode ? '�v' : '';
        my $private_browsing_mode_matched_str = $private_browsing_mode_matched_flag ? '�v' : '';

        # ��������
        my $res_length_str = $log_only || $res_length;

        # �摜������
        my $upfile_count_str = $upfile_count > 0 ? "${upfile_count}��" : '';

        # �ǉ����郍�O�s���쐬
        $log_add_contents = join(',',
            map { Encode::is_utf8($_) ? $_ : $enc_cp932->decode($_) } (
                $date, # ����
                $cookie_a_issuing_str, # CookieA���s
                $private_browsing_mode_matched_str, # �v���C�x�[�g����
                $add_match_time_range, # ��v����
                $add_match_period, # ���Ԏw��
                $status, # �X�e�[�^�X
                $title_exempt, # �X���^�C���O
                $exempt, # ���O
                $force_prohibit, # ����
                $url, # URL
                $category, # �J�e�S��
                '��',
                $add_match_title, # ��v�X���^�C
                $add_match_title_exempt_on_thread_create, # �X���^�C�����̏��O
                $add_match_suppress_thread_creation_title, # ��v�X���^�C(�}��)
                $add_match_suppress_thread_creation_res, # ��v���X(�}��)
                '��',
                $add_match_name, # ��v���O
                '��',
                $res_length_str, # ������
                $add_match_concat_res, # �Ώۂ̃��X
                $add_match_res, # ��v���X
                $add_match_res_length_exempt, # ���������O (�����������݋֎~�@�\(���X))
                $add_match_up_to_res, # �w�背�X�Ԃ܂ł̈�v���X
                $add_match_up_to_res_res_length_exempt, # ���������O (�w�肵�����XNo�܂ł̎����������݋֎~�@�\)
                $add_match_multiple_submissions, # �����񃌃X
                $add_old_thread_age, # �ÃX��age
                '��',
                $add_res_exempt_on_thread_create_match_title, # �X���쐬���̃X���^�C�ɂ�郌�X�̏��O�i�X���j
                $add_res_exempt_on_thread_create_match_res, # �X���쐬���̃X���^�C�ɂ�郌�X�̏��O�i���X�j
                $add_res_exempt_on_res_match_title, # �X���^�C�ɂ�郌�X�̏��O(�X��)
                $add_res_exempt_on_res_match_res, # �X���^�C�ɂ�郌�X�̏��O(���X)
                $add_res_exempt_on_res_match_up_to_res_num_exempt, # �w�背�X�܂ŏ��O
                '��',
                $add_force_title_match_on_thread_create, # �X���쐬���̃X���^�C������v
                $add_force_res_match_on_thread_create_title, # �X���쐬���̋�����v���X(�X��)
                $add_force_res_match_on_thread_create_res, # �X���쐬���̋�����v���X(���X)
                $add_force_res_match_on_res_title, # �X���^�C�ɂ�鋭����v���X(�X��)
                $add_force_res_match_on_res_res, # �X���^�C�ɂ�鋭����v���X(���X)
                $add_img_upl_match_flag, # �摜�A�b�v
                '��',
                $add_match_cookiea, # ��vCookieA
                $add_match_userid, # ��v�o�^ID
                $add_match_historyid, # ��v����ID
                $add_match_host, # ��v�z�X�g
                $add_match_useragent, # ��vUserAgent
                $add_match_img_md5, # ��vMD5
                $add_match_img_md5_comment, # ��v�摜�R�����g
                '��',
                $add_title, # �X���^�C
                $add_name, # ���O
                $add_res, # ���X���e
                $upfile_count_str, # �摜����
                $private_browsing_mode_str, # �v���C�x�[�g
                defined($cookie_a) && $cookie_a ne '' ? $thread_create_suppress_str . $cookie_a : '', # CookieA
                defined($user_id) && $user_id ne '' ? $thread_create_suppress_str . $user_id : '', # �o�^ID
                defined($history_id) && $history_id ne '' ? $thread_create_suppress_str . $history_id : '', # ����ID
                $host ne '' ? $thread_create_suppress_str . $host : '', # �z�X�g
                $useragent, # UserAgent
                $time, # �^�C���X�^���v
                $idcrypt  # ID
            )
        ) . "\n";
    }

    # �K�v�ɉ����ă��O�t�@�C���ɏ�������
    write_log($self, $log_add_contents);

    # �����񓊍e���̎����������݋֎~�@�\ ���[�U�[�J�E���g���O�ɏ�������
    if ($multiple_submissions_log_add_flag) {
        write_multiple_submissions_log($self);
    }

    # �ÃX��age�̎����������݋֎~�@�\ �ÃX��age���[�U�[�J�E���g���O�ɏ�������
    if ($old_thread_age_log_add_flag) {
        write_old_thread_age_log($self);
    }

    # ���茋�ʂ�Ԃ�
    my $result = RESULT_ALL_PASSED;
    if ($suppress_thread_creation_flag) {
        # �X���b�h�쐬�}���Ώ�
        $result |= RESULT_THREAD_CREATE_SUPPRESS_REQUIRED;
    }
    if ($redirect_flag) {
        # ���_�C���N�g�Ώ�
        $result |= RESULT_REDIRECT_REQUIRED;
    }
    return $result;
}

# ���O�o�͍��ڌ����T�u���[�`����`
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

# ���O�������݃T�u���[�`����`
sub write_log {
    my ($self, $log_add_contents) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }
    arg_check(2, ['AutoPostProhibit', undef], @_);

    # ���O�t�@�C���n���h���[�擾
    my $log_fh = $self->('LOG_FH');
    my $no_delete_log_fh = $self->('NO_DELETE_LOG_FH');

    # �w�b�_�[��`
    my $header_str = join(',', @log_header) . "\n${log_second_header_row}\n";

    # �������O��������
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

    # �ݐσ��O��������
    # (�ݐσ��O�V�K�쐬���E�t�@�C���T�C�Y��0�̎��́A�\�߃w�b�_�[��ǉ�)
    if ($self->('NEW_NO_DELETE_LOG_FLAG')) {
        print $no_delete_log_fh $header_str;
    }
    if (defined($log_add_contents)) {
        seek($no_delete_log_fh, 0, 2);
        print $no_delete_log_fh $log_add_contents;
    }

    # ���O�t�@�C���N���[�Y
    close($log_fh);
    close($no_delete_log_fh);
};

# �����񓊍e���̎����������݋֎~�@�\ ���[�U�[�J�E���g���O�������݃T�u���[�`����`
sub write_multiple_submissions_log {
    my ($self) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }
    arg_check(1, ['AutoPostProhibit'], @_);

    # ���O�t�@�C���n���h���擾
    my $multiple_submissions_count_log_fh = $self->('MULTIPLE_SUBMISSIONS_COUNT_LOG_FH');

    # ��������
    seek($multiple_submissions_count_log_fh, 0, 0);
    foreach my $validlog_array_ref (@{$self->('MULTIPLE_SUBMISSIONS_VALIDLOG_ARRAY_REF')}) {
        print $multiple_submissions_count_log_fh join($multiple_submissions_count_log_delimiter, @{$validlog_array_ref}) . "\n";
    }
    truncate($multiple_submissions_count_log_fh, tell($multiple_submissions_count_log_fh));

    # �N���[�Y
    close($multiple_submissions_count_log_fh);
}

# �ÃX��age�̎����������݋֎~�@�\ �ÃX��age���[�U�[�J�E���g���O�������݃T�u���[�`����`
sub write_old_thread_age_log {
    my ($self) = @_;
    if ((caller)[0] ne (caller(0))[0]) {
        confess('call me only in instance subroutine.');
    }
    arg_check(1, ['AutoPostProhibit'], @_);

    # ���O�t�@�C���n���h���擾
    my $old_thread_age_count_log_fh = $self->('OLD_THREAD_AGE_COUNT_LOG_FH');

    # ��������
    seek($old_thread_age_count_log_fh, 0, 0);
    foreach my $validlog_array_ref (@{$self->('OLD_THREAD_AGE_VALIDLOG_ARRAY_REF')}) {
        print $old_thread_age_count_log_fh join($old_thread_age_count_log_delimiter, @{$validlog_array_ref}) . "\n";
    }
    truncate($old_thread_age_count_log_fh, tell($old_thread_age_count_log_fh));

    # �N���[�Y
    close($old_thread_age_count_log_fh);
}

1;
