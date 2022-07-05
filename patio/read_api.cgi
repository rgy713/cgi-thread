#!/usr/local/bin/perl

BEGIN {
    # �O���t�@�C����荞��
    require './init.cgi';
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use JSON::XS;
use HistoryCookie;
use HistoryLog;

# �����擾
my ($time) = get_time();

# HTTP�X�e�[�^�X�R�[�h��`
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
    # POST�ȊO�̃A�N�Z�X������(405 Method Not Allowed��Ԃ�)
    output_http_header($HTTP_STATUS_405_METHOD_NOT_ALLOWED);
    exit();
} elsif (!exists($ENV{CONTENT_TYPE}) || $ENV{CONTENT_TYPE} !~ /^application\/json(?:;.*|\s*)?$/) {
    # Content-Type��application/json�ȊO�̃A�N�Z�X������(415 Unsupported Media Type��Ԃ�)
    output_http_header($HTTP_STATUS_415_UNSUPPORTED_MEDIA_TYPE);
    exit();
}

# POST���ꂽpayload��URL�f�R�[�h���Ď擾
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

# JSON�p�[�X
my $json = {};
eval {
    if (defined($payload)) {
        $json = JSON::XS->new()->utf8(1)->decode($payload);
    }
};
if ($@) {
    # Payload���������Ȃ��Ȃǂ�JSON�f�R�[�h�ł��Ȃ��ꍇ�́A400 Bad Request��Ԃ�
    output_http_header($HTTP_STATUS_400_BAD_REQUEST);
    exit();
}

# �G���[�o�͏I���t���O
my $error_output_flg = 1;

# �����܂œǂ񂾋@�\ �X���b�h�ǉ�
if ($json->{mode} eq 'readup_to_here' && int($json->{thread_no}) > 0) {
    # ����ID���擾
    my $chistory_id = do {
        my $instance = HistoryCookie->new();
        $instance->get_history_id();
    };
    if (!defined($chistory_id)) {
        # ����ID���O�C�����ĂȂ��ꍇ�́A403 Forbidden��Ԃ�
        output_http_header($HTTP_STATUS_403_FORBIDDEN);
        exit();
    }

    # HistoryLog�C���X�^���X��������
    my $history_log = HistoryLog->new($chistory_id);

    # �ŐV���X�����X���b�h���O����擾
    my @log;
    {
        # �X���b�h���O�ꊇ�ǂݍ���
        # �X���b�h���O�t�@�C����������Ȃ��ꍇ�� 401 Gone���A
        # �X���b�h���O�t�@�C�������b�N�ł��Ȃ��ꍇ�́A503 Service Unavailable��Ԃ�
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
        # ���O�s��2�s�����̏ꍇ�A�X���b�h���O�����݂��Ȃ��������̂Ƃ݂Ȃ��A410 Gone��Ԃ�
        output_http_header($HTTP_STATUS_410_GONE);
        exit();
    }
    my $decoded_sub = $enc_cp932->decode(${$log[0]}[1]);
    my ($latest_res_no, $latest_res_time) = @{$log[$#log]}[0, 11];

    # �������ݗ����@�\�̏��O�ݒ荇�v����
    if (scalar(grep { $_ ne '' && index($decoded_sub, $_) != -1 } @history_save_exempt_titles) > 0) {
        # ���O�Ώۂ������ꍇ�A404 Not Found��Ԃ�
        output_http_header($HTTP_STATUS_404_NOT_FOUND);
        exit();
    }

    # �������O�ɒǉ����A�����X�e�[�^�X�R�[�h��Ԃ�
    $history_log->add_post_history($json->{thread_no}, $latest_res_no, $latest_res_time);
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # HistoryLog�C���X�^���X ���
    $history_log->DESTROY();

    # ����I��
    $error_output_flg = 0;
}

# �X���b�hNo�������������݋֎~�@�\�̃��X���������œ��삷��@�\
if ($json->{mode} eq 'thread_num_auto_prohibiting'
    && $json->{thread_number} > 0
    && (   $json->{action} eq 'add_1' || $json->{action} eq 'add_2' || $json->{action} eq 'add_3'
        || $json->{action} eq 'add_4' || $json->{action} eq 'add_5' || $json->{action} eq 'add_6'
        || $json->{action} eq 'add_permanently'
        || $json->{action} eq 'remove'
        )
    ) {

    # ���O�t�@�C�����p�[�X����K�v�����邩�ǂ���
    my $need_parse_log = -s $auto_post_prohibit_thread_number_res_target_log_path > 2;

    # ���O�t�@�C���I�[�v��
    open(my $json_log_fh, '+>>', $auto_post_prohibit_thread_number_res_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS �C���X�^���X������
    my $json_serializer = JSON::XS->new();

    # ���O�t�@�C���ǂݍ��݁E�p�[�X����
    my @load_thread_number_res_target_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_thread_number_res_target_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # 500 Internal Server Error��Ԃ�
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # �p�[�X�����z��̐����ݒ�n�b�V���̂����A���O�t�@�C���ɕۑ����鐧���ݒ�n�b�V���z����쐬
    my @save_thread_number_res_target_array;
    foreach my $target_hash_ref (@load_thread_number_res_target_array) {
        # �n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
        if (ref($target_hash_ref) ne 'HASH') {
            next;
        }
        my %target_hash = %{$target_hash_ref};

        # �K�{�L�[�������A�ݒ莞�Ԃ��o�߂����ݒ�A�ǉ�/�폜����X���b�h�ԍ��Ɠ����ݒ�̓X�L�b�v
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

        # ���O�t�@�C���Ɏc��
        push(@save_thread_number_res_target_array, $target_hash_ref);
    }

    # �ǉ����[�h�̂݁A�����ݒ��ǉ�
    if ($json->{action} ne 'remove') {
        # type�l����
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

        # �ǉ��f�[�^���쐬
        my %data = (
            thread_number => int($json->{thread_number}),
            time          => $time,
            type          => $type
        );

        # �����ݒ��ǉ�
        push(@save_thread_number_res_target_array, \%data);
    }

    # ���O�t�@�C�����X�V
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_thread_number_res_target_array);

    # ���O�t�@�C���N���[�Y
    close($json_log_fh);

    # �����X�e�[�^�X�R�[�h��Ԃ�
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # ����I��
    $error_output_flg = 0;
}

# �X���b�h�^�C�g���������������݋֎~�@�\�̃��X���������œ��삷��@�\
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
    # ���O�t�@�C�����p�[�X����K�v�����邩�ǂ���
    my $need_parse_log = -s $auto_post_prohibit_thread_title_res_target_log_path > 2;

    # ���O�t�@�C���I�[�v��
    open(my $json_log_fh, '+>>', $auto_post_prohibit_thread_title_res_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS �C���X�^���X������
    my $json_serializer = JSON::XS->new();

    # ���O�t�@�C���ǂݍ��݁E�p�[�X����
    my @load_thread_title_res_target_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_thread_title_res_target_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # 500 Internal Server Error��Ԃ�
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # �p�[�X�����z��̐����ݒ�n�b�V���̂����A���O�t�@�C���ɕۑ����鐧���ݒ�n�b�V���z����쐬
    my @save_thread_title_res_target_array;
    foreach my $target_hash_ref (@load_thread_title_res_target_array) {
        # �n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
        if (ref($target_hash_ref) ne 'HASH') {
            next;
        }
        my %target_hash = %{$target_hash_ref};

        # �ُ�ݒ�l�A�ݒ莞�Ԃ��o�߂����ݒ�A�ǉ�/�폜����X���b�h�^�C�g���E�����P��Ɠ����ݒ�̓X�L�b�v
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

        # ���O�t�@�C���Ɏc��
        push(@save_thread_title_res_target_array, $target_hash_ref);
    }

    # �ǉ����[�h�̂݁A�����ݒ��ǉ�
    if ($json->{action} ne 'remove') {
        # type�l����
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

        # �ǉ�
        push(@save_thread_title_res_target_array, {
                thread_title => $json->{thread_title},
                type         => $type,
                time         => $time,
                word_type    => $json->{word_type}
            });
    }

    # ���O�t�@�C�����X�V
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_thread_title_res_target_array);

    # ���O�t�@�C���N���[�Y
    close($json_log_fh);

    # �����X�e�[�^�X�R�[�h��Ԃ�
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # ����I��
    $error_output_flg = 0;
}

# �X���b�h��ʂ��烆�[�U�𐧌�����@�\
# ���[�U�����@�\ (CookieA�Ȃǂ��t�H�[������o�^)
if (($json->{mode} eq 'restrict_user_from_thread_page' || $json->{mode} eq 'restrict_user_from_form')
    && ($json->{action} eq 'add_1' || $json->{action} eq 'add_2'
        || $json->{action} eq 'add_3' || $json->{action} eq 'add_4'
        || $json->{action} eq 'add_5' || $json->{action} eq 'add_6'
        || $json->{action} eq 'add_7'
        || $json->{action} eq 'add_permanently' || $json->{action} eq 'remove')) {
    # ����ID�������Ă����ꍇ�́A���炩���ߖ�����@���폜����
    if (exists($json->{history_id})) {
        $json->{history_id} =~ s/\@$//;
    }

    # ���O�t�@�C�����p�[�X����K�v�����邩�ǂ���
    my $need_parse_log = -s $restrict_user_from_thread_page_target_log_path > 2;

    # ���O�t�@�C���I�[�v��
    open(my $json_log_fh, '+>>', $restrict_user_from_thread_page_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS �C���X�^���X������
    my $json_serializer = JSON::XS->new();

    # ���O�t�@�C���ǂݍ��݁E�p�[�X����
    my @load_restrict_user_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_restrict_user_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # 500 Internal Server Error��Ԃ�
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # �p�[�X�����z��̐����ݒ�n�b�V���̂����A���O�t�@�C���ɕۑ����鐧���ݒ�n�b�V���z����쐬
    my @save_restrict_user_array;
    foreach my $setting_ref (@load_restrict_user_array) {
        # �n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
        if (ref($setting_ref) ne 'HASH') {
            next;
        }

        # �ُ�ݒ�l�A�ݒ莞�Ԃ��o�߂����ݒ�̓X�L�b�v
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

        # �����̐ݒ肩��A�ǉ�/�폜����ۂɕ�����v����ݒ���폜
        foreach my $key ('cookie_a', 'history_id', 'host', 'user_id') {
            if ($setting_ref->{$key} ne '' && $setting_ref->{$key} eq $json->{$key}) {
                delete($setting_ref->{$key});
            }
        }
        if (scalar(keys(%{$setting_ref})) < 3) {
            # �������ڂ��c��Ȃ������ݒ�̓X�L�b�v
            next;
        }

        # ���O�t�@�C���Ɏc��
        push(@save_restrict_user_array, $setting_ref);
    }

    # �ǉ����[�h�̂݁A�����ݒ��ǉ�
    if ($json->{action} ne 'remove') {
        # type�l����
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

        # �ǉ��ΏۃL�[������
        my @target = grep { $json->{$_} ne '' } ('cookie_a', 'history_id', 'user_id');
        if ($json->{host} ne ''
            && scalar(grep { $_ ne '' && index($json->{host}, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0) {
            # �z�X�g�́A@ngthread_thread_list_creator_name_override_exclude_hosts�ɕ�����v���Ȃ��ꍇ�̂ݒǉ��ΏۂƂ���
            push(@target, 'host');
        }

        # �ǉ�
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

    # ���O�t�@�C�����X�V
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_restrict_user_array);

    # ���O�t�@�C���N���[�Y
    close($json_log_fh);

    # �����X�e�[�^�X�R�[�h��Ԃ�
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # ����I��
    $error_output_flg = 0;
}

# �X���b�h��ʂ��烆�[�U�����Ԑ�������@�\
if ($json->{mode} eq 'restrict_user_from_thread_page_by_time_range'
    && ($json->{action} eq 'add_1' || $json->{action} eq 'add_2'
        || $json->{action} eq 'add_3' || $json->{action} eq 'add_4'
        || $json->{action} eq 'add_permanently' || $json->{action} eq 'remove')) {
    # ����ID�������Ă����ꍇ�́A���炩���ߖ�����@���폜����
    if (exists($json->{history_id})) {
        $json->{history_id} =~ s/\@$//;
    }

    # ���O�t�@�C�����p�[�X����K�v�����邩�ǂ���
    my $need_parse_log = -s $restrict_user_from_thread_page_by_time_range_target_log_path > 2;

    # ���O�t�@�C���I�[�v��
    open(my $json_log_fh, '+>>', $restrict_user_from_thread_page_by_time_range_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS �C���X�^���X������
    my $json_serializer = JSON::XS->new();

    # ���O�t�@�C���ǂݍ��݁E�p�[�X����
    my @load_restrict_user_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_restrict_user_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # 500 Internal Server Error��Ԃ�
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # �p�[�X�����z��̐����ݒ�n�b�V���̂����A���O�t�@�C���ɕۑ����鐧���ݒ�n�b�V���z����쐬
    my @save_restrict_user_array;
    foreach my $setting_ref (@load_restrict_user_array) {
        # �n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
        if (ref($setting_ref) ne 'HASH') {
            next;
        }

        # �ُ�ݒ�l�A�ݒ莞�Ԃ��o�߂����ݒ�̓X�L�b�v
        if (!exists($setting_ref->{type}) || $setting_ref->{type} < 0 || $setting_ref->{type} > 4
            || !exists($setting_ref->{time}) || $setting_ref->{time} < 0
            || ($setting_ref->{type} == 1 && (($setting_ref->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_1 * 3600) < $time))
            || ($setting_ref->{type} == 2 && (($setting_ref->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_2 * 3600) < $time))
            || ($setting_ref->{type} == 3 && (($setting_ref->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_3 * 3600) < $time))
            || ($setting_ref->{type} == 4 && (($setting_ref->{time} + $restrict_user_from_thread_page_by_time_range_target_hold_hour_4 * 3600) < $time))
            || ($setting_ref->{cookie_a} eq '' && $setting_ref->{history_id} eq '' && $setting_ref->{host} eq '' && $setting_ref->{user_id} eq '')) {
            next;
        }

        # �����̐ݒ肩��A�ǉ�/�폜����ۂɕ�����v����ݒ���폜
        foreach my $key ('cookie_a', 'history_id', 'host', 'user_id') {
            if ($setting_ref->{$key} ne '' && $setting_ref->{$key} eq $json->{$key}) {
                delete($setting_ref->{$key});
            }
        }
        if (scalar(keys(%{$setting_ref})) < 3) {
            # �������ڂ��c��Ȃ������ݒ�̓X�L�b�v
            next;
        }

        # ���O�t�@�C���Ɏc��
        push(@save_restrict_user_array, $setting_ref);
    }

    # �ǉ����[�h�̂݁A�����ݒ��ǉ�
    if ($json->{action} ne 'remove') {
        # type�l����
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

        # �ǉ��ΏۃL�[������
        my @target = grep { $json->{$_} ne '' } ('cookie_a', 'history_id', 'user_id');
        if ($json->{host} ne ''
            && scalar(grep { $_ ne '' && index($json->{host}, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0) {
            # �z�X�g�́A@ngthread_thread_list_creator_name_override_exclude_hosts�ɕ�����v���Ȃ��ꍇ�̂ݒǉ��ΏۂƂ���
            push(@target, 'host');
        }

        # �ǉ�
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

    # ���O�t�@�C�����X�V
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_restrict_user_array);

    # ���O�t�@�C���N���[�Y
    close($json_log_fh);

    # �����X�e�[�^�X�R�[�h��Ԃ�
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # ����I��
    $error_output_flg = 0;
}

# �X���b�h��ʂ��烆�[�U�𐧌�����@�\ (���̃X���̂�)
if ($json->{mode} eq 'in_thread_only_restrict_user_from_thread_page'
    && $json->{thread_number} > 0
    && ($json->{action} eq 'add' || $json->{action} eq 'remove')) {
    # ����ID�������Ă����ꍇ�́A���炩���ߖ�����@���폜����
    if (exists($json->{history_id})) {
        $json->{history_id} =~ s/\@$//;
    }

    # ���O�t�@�C�����p�[�X����K�v�����邩�ǂ���
    my $need_parse_log = -s $in_thread_only_restrict_user_from_thread_page_target_log_path > 2;

    # ���O�t�@�C���I�[�v��
    open(my $json_log_fh, '+>>', $in_thread_only_restrict_user_from_thread_page_target_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS �C���X�^���X������
    my $json_serializer = JSON::XS->new();

    # ���O�t�@�C���ǂݍ��݁E�p�[�X����
    my %load_restrict_user_hash;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'HASH') {
                %load_restrict_user_hash = %{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # 500 Internal Server Error��Ԃ�
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # �p�[�X���������ݒ�n�b�V���̂����A���O�t�@�C���ɕۑ����鐧���ݒ�n�b�V���z����쐬
    my %save_restrict_user_hash;
    while (my ($thread_number, $settings_array_ref) = each(%load_restrict_user_hash)) {
        # �ُ�X���b�hNo�̓X�L�b�v
        if ($thread_number <= 0) {
            next;
        }
        # �l���z�񃊃t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
        if (ref($settings_array_ref) ne 'ARRAY') {
            next;
        }

        # �����X���b�hNo���ǂ���
        my $is_same_thread_number = $thread_number == $json->{thread_number};

        # �ۑ��Ώ� �X���b�hNo�������ݒ�n�b�V���̔z��
        my @save_restrict_user_hash_array_in_thread;

        # �X���b�hNo�� �����ݒ�z�񃋁[�v
        foreach my $setting_ref (@{$settings_array_ref}) {
            # �n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
            if (ref($setting_ref) ne 'HASH') {
                next;
            }

            # �ُ�ݒ�l�A�ݒ莞�Ԃ��o�߂����ݒ�̓X�L�b�v
            if (!exists($setting_ref->{time}) || $setting_ref->{time} < 0
                || (($setting_ref->{time} + $in_thread_only_restrict_user_from_thread_page_target_hold_hour * 3600) < $time)
                || ($setting_ref->{cookie_a} eq '' && $setting_ref->{history_id} eq '' && $setting_ref->{host} eq '' && $setting_ref->{user_id} eq '')) {
                next;
            }

            # �����X���b�hNo�̏ꍇ�ɁA�����̐ݒ肩��A�ǉ�/�폜����ۂɕ�����v����ݒ���폜
            if ($is_same_thread_number) {
                foreach my $key ('cookie_a', 'history_id', 'host', 'user_id') {
                    if ($setting_ref->{$key} ne '' && $setting_ref->{$key} eq $json->{$key}) {
                        delete($setting_ref->{$key});
                    }
                }
            }

            # �������ڂ��c��Ȃ������ݒ�̓X�L�b�v
            if (scalar(keys(%{$setting_ref})) < 2) {
                next;
            }

            # �ۑ��Ώ� �X���b�hNo�������ݒ�z��ɒǉ�
            push(@save_restrict_user_hash_array_in_thread, $setting_ref);
        }

        # �ۑ��Ώ� �X���b�hNo�������ݒ�n�b�V���z���1�ȏ�ݒ肪����Ƃ��́A
        # ���O�ۑ������ݒ�n�b�V���ɒǉ�
        if (scalar(@save_restrict_user_hash_array_in_thread) > 0) {
            $save_restrict_user_hash{$thread_number} = \@save_restrict_user_hash_array_in_thread;
        }
    }

    # �ǉ����[�h�̂݁A�����ݒ��ǉ�
    if ($json->{action} ne 'remove') {
        # �ǉ��ΏۃL�[������
        my @target = grep { $json->{$_} ne '' } ('cookie_a', 'history_id', 'user_id');
        if ($json->{host} ne ''
            && scalar(grep { $_ ne '' && index($json->{host}, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0) {
            # �z�X�g�́A@ngthread_thread_list_creator_name_override_exclude_hosts�ɕ�����v���Ȃ��ꍇ�̂ݒǉ��ΏۂƂ���
            push(@target, 'host');
        }

        # �ǉ�
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

    # ���O�t�@�C�����X�V
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\%save_restrict_user_hash);

    # ���O�t�@�C���N���[�Y
    close($json_log_fh);

    # �����X�e�[�^�X�R�[�h��Ԃ�
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # ����I��
    $error_output_flg = 0;
}

# ���[�U�����\���@�\
if (($json->{mode} eq 'highlight_userinfo' || $json->{mode} eq 'highlight_userinfo_from_form')
    && ($json->{action} eq 'add' || $json->{action} eq 'remove')) {
    # ����ID�������Ă����ꍇ�́A���炩���ߖ�����@���폜����
    if (exists($json->{history_id})) {
        $json->{history_id} =~ s/\@$//;
    }

    # ���O�t�@�C�����p�[�X����K�v�����邩�ǂ���
    my $need_parse_log = -s $highlight_userinfo_log_path > 2;

    # ���O�t�@�C���I�[�v��
    open(my $json_log_fh, '+>>', $highlight_userinfo_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS �C���X�^���X������
    my $json_serializer = JSON::XS->new();

    # ���O�t�@�C���ǂݍ��݁E�p�[�X����
    my @load_highlight_hashref_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_highlight_hashref_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # 500 Internal Server Error��Ԃ�
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # �p�[�X���������\�����n�b�V�����t�@�����X�z����A���O�t�@�C���ɕۑ�������݂̂̂ƂȂ�悤�t�B���^
    my @save_highlight_hashref_array;
    foreach my $highlight_hashref (@load_highlight_hashref_array) {
        # �l���n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
        if (ref($highlight_hashref) ne 'HASH') {
            next;
        }

        # �����\���^�C�v���Z�b�g����Ă��Ȃ��ꍇ�A���[�U�����\���Ƃ݂Ȃ�
        if (!exists($highlight_hashref->{type})) {
            $highlight_hashref->{type} = 1;
        }

        # �����\���^�C�v�����[�U�����\���������ꍇ�A�t�B���^�[����
        # ����ȊO�̋����\���^�C�v�͂��̂܂܂Ƃ���
        if ($highlight_hashref->{type} == 1) {
            # �ُ�ݒ�l�A�ݒ莞�Ԃ��o�߂����ݒ�̓X�L�b�v
            if (!exists($highlight_hashref->{time}) || $highlight_hashref->{time} < 0
                || ($highlight_hashref->{time} + $highlight_userinfo_hold_hour * 3600) <= $time
                || !exists($highlight_hashref->{color}) || $highlight_hashref->{color} < 1
                || ($highlight_hashref->{cookie_a} eq '' && $highlight_hashref->{history_id} eq '' && $highlight_hashref->{host} eq '' && $highlight_hashref->{user_id} eq '')) {
                next;
            }

            # �����̐ݒ肩��A�ǉ�/�폜����ۂɕ�����v����ݒ���폜
            foreach my $key ('cookie_a', 'history_id', 'host', 'user_id') {
                if ($highlight_hashref->{$key} ne '' && $highlight_hashref->{$key} eq $json->{$key}) {
                    delete($highlight_hashref->{$key});
                }
            }

            # �������ڂ��c��Ȃ������ݒ�̓X�L�b�v
            if (scalar(keys(%{$highlight_hashref})) < 4) {
                next;
            }
        }

        # �ۑ��Ώ� �����\�����n�b�V�����t�@�����X�z��ɒǉ�
        push(@save_highlight_hashref_array, $highlight_hashref);
    }

    # �ǉ����[�h�̂݁A�����\���ݒ��ǉ�
    if ($json->{action} eq 'add') {
        # �ǉ��ΏۃL�[������
        my @target = grep { $json->{$_} ne '' } ('cookie_a', 'history_id', 'user_id');
        if ($json->{host} ne ''
            && scalar(grep { $_ ne '' && index($json->{host}, $_) >= 0 } @ngthread_thread_list_creator_name_override_exclude_hosts) == 0) {
            # �z�X�g�́A@ngthread_thread_list_creator_name_override_exclude_hosts�ɕ�����v���Ȃ��ꍇ�̂ݒǉ��ΏۂƂ���
            push(@target, 'host');
        }

        # �ǉ�
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

    # ���O�t�@�C�����X�V
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_highlight_hashref_array);

    # ���O�t�@�C���N���[�Y
    close($json_log_fh);

    # �����X�e�[�^�X�R�[�h��Ԃ�
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # ����I��
    $error_output_flg = 0;
}

# UserAgent�̋����\���@�\
if ($json->{mode} eq 'highlight_ua_from_form'
    && ($json->{action} eq 'add' || $json->{action} eq 'update_timestamp' || $json->{action} eq 'remove')
    && $json->{host} ne ''
    && $json->{useragent} ne '') {

    # ���O�t�@�C�����p�[�X����K�v�����邩�ǂ���
    my $need_parse_log = -s $highlight_userinfo_log_path > 2;

    # ���O�t�@�C���I�[�v��
    open(my $json_log_fh, '+>>', $highlight_userinfo_log_path) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();
    flock($json_log_fh, 2) || output_http_header($HTTP_STATUS_503_SERVICE_UNAVAILABLE) && exit();

    # JSON::XS �C���X�^���X������
    my $json_serializer = JSON::XS->new();

    # ���O�t�@�C���ǂݍ��݁E�p�[�X����
    my @load_highlight_hashref_array;
    if ($need_parse_log) {
        seek($json_log_fh, 0, 0);
        local $/;
        my $json_log_contents = <$json_log_fh>;

        # JSON�p�[�X���s��
        eval {
            my $json_parsed_ref = $json_serializer->utf8(1)->decode($json_log_contents);
            if (ref($json_parsed_ref) eq 'ARRAY') {
                @load_highlight_hashref_array = @{$json_parsed_ref};
            }
        };
        if ($@) {
            # JSON�p�[�X�Ɏ��s���� (���e�Ɉُ킪����)�ꍇ�A
            # 500 Internal Server Error��Ԃ�
            close($json_log_fh);
            output_http_header($HTTP_STATUS_500_INTERNAL_SERVER_ERROR);
            exit();
        }
    }

    # �p�[�X���������\�����n�b�V�����t�@�����X�z����A���O�t�@�C���ɕۑ�������݂̂̂ƂȂ�悤�t�B���^
    my @save_highlight_hashref_array;
    my $modified_flag;
    foreach my $highlight_hashref (@load_highlight_hashref_array) {
        # �l���n�b�V�����t�@�����X�ł͂Ȃ��ꍇ�̓X�L�b�v
        if (ref($highlight_hashref) ne 'HASH') {
            next;
        }

        # �����\���^�C�v���Z�b�g����Ă��Ȃ��ꍇ�A���[�U�����\���Ƃ݂Ȃ�
        if (!exists($highlight_hashref->{type})) {
            $highlight_hashref->{type} = 1;
        }

        # �����\���^�C�v��UserAgent�����\���������ꍇ�A�t�B���^�[����
        # ����ȊO�̋����\���^�C�v�͂��̂܂܂Ƃ���
        if ($highlight_hashref->{type} == 2) {
            # �ُ�ݒ�l�̓X�L�b�v
            if (!exists($highlight_hashref->{time}) || $highlight_hashref->{time} < 0
                || !exists($highlight_hashref->{color}) || $highlight_hashref->{color} < 1
                || ($highlight_hashref->{host} eq '' && $highlight_hashref->{useragent} eq '')) {
                next;
            }

            # �����z�X�g�E����UserAgent�̐ݒ肪�����Ă����ꍇ�ɁA
            # �o�^�E�폜�ł́A���̐ݒ���X�L�b�v�A
            # �^�C���X�^���v�X�V�ł́A�^�C���X�^���v���X�V����
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

        # �ۑ��Ώ� �����\�����n�b�V�����t�@�����X�z��ɒǉ�
        push(@save_highlight_hashref_array, $highlight_hashref);
    }

    if ($json->{action} eq 'add') {
        # �ǉ����[�h�̂݁A�����\���ݒ��ǉ�
        my $add_hashref = {
            color     => int($json->{color}),
            host      => $json->{host},
            time      => $time,
            type      => 2,
            useragent => $json->{useragent}
        };
        unshift(@save_highlight_hashref_array, $add_hashref); # ��v����̍ہA�V�����ݒ�̈�v��D�悳���邽�߁A�擪�ɒǉ�

        # �ݒ莞�Ԃ��o�߂����ݒ������
        @save_highlight_hashref_array = grep { ($_->{time} + $highlight_ua_hold_hour * 3600) > $time } @save_highlight_hashref_array;
    } elsif (!$modified_flag) {
        # �^�C���X�^���v�X�V�E�폜�Ώۂ�������Ȃ��������߁A404 Not Found��Ԃ�
        close($json_log_fh);
        output_http_header($HTTP_STATUS_404_NOT_FOUND);
        exit();
    }

    # ���O�t�@�C�����X�V
    seek($json_log_fh, 0, 0);
    truncate($json_log_fh, 0);
    print $json_log_fh $json_serializer->utf8(1)->encode(\@save_highlight_hashref_array);

    # ���O�t�@�C���N���[�Y
    close($json_log_fh);

    # �����X�e�[�^�X�R�[�h��Ԃ�
    output_http_header($HTTP_STATUS_204_NO_CONTENT);

    # ����I��
    $error_output_flg = 0;
}

# �s�K�؂Ȓl�������Ă����ȂǁA�G���[�I���t���O���������܂܂̏ꍇ�́A400 Bad Request��Ԃ�
if ($error_output_flg) {
    output_http_header($HTTP_STATUS_400_BAD_REQUEST);
    exit();
}

# HTTP�X�e�[�^�X�R�[�h�o�̓T�u���[�`��
# (�t�@�C���㕔�Œ�`���Ă���ϐ���HTTP�X�e�[�^�X�R�[�h�Ƃ��Ĉ����Ɏg�p���ĉ�����)
sub output_http_header {
    my ($http_status_code) = @_;
    print $http_status_code
            . "Cache-Control: private, no-store, no-cache, must-revalidate\n"
            . "Pragma: no-cache\n\n";
}
