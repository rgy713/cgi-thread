package HistoryLog;
use strict;
use Encode;
use File::Spec;
use JSON::XS;

# �����̏������ݗ������O�ŁA�X���b�h���O�����݂���X���b�h�݂̂ƂȂ�悤�t�B���^�����O
my $validate_post_histories = sub {
    my ($self, $dont_perform_save) = @_;

    if (defined(my $post_history_array_ref = $self->('PostHistory'))) {
        # �t�B���^�����O���s�O�̗v�f�����擾
        my $before_validate_elements_count = scalar(@{$post_history_array_ref});

        # �X���b�h���O�t�@�C�������݂��Ȃ��v�f�͏��O
        my @post_history = grep {
            my $log_thread_no = ${$_}[0];
            my $logfile_path = main::get_logfolder_path($log_thread_no) . "/$log_thread_no.cgi";
            -r $logfile_path;
        } @{$post_history_array_ref};

        # �t�B���^�����O���s�O��ŗv�f�����ω������ꍇ�̂݁A�������ݗ������O���A�b�v�f�[�g
        if (scalar(@post_history) != $before_validate_elements_count) {
            if (scalar(@post_history) > 0) {
                # �������ݗ������O���A�b�v�f�[�g
                $self->('PostHistory', \@post_history, $dont_perform_save);
            } else {
                # �������ݗ������O��1�����Ȃ��̂ŁA�L�[���ƍ폜
                $self->('PostHistory', undef, $dont_perform_save);
            }
        }
    }
};

sub new {
    my ($class, $history_id) = @_;
    my $self = {};

    # JSON::XS�C���X�^���X������
    my $json = JSON::XS->new();

    # ����ID���O�t�@�C���p�X����
    my $history_log_filepath = do {
        (my $folder_number = $history_id) =~ s/^([0-9]{2}).*/$1/;
        File::Spec->catfile($main::history_shared_conf{history_logdir}, $folder_number, "$history_id.log");
    };

    # ����ID���O�t�@�C���I�[�v��
    open(my $history_log_fh, '+>>', $history_log_filepath) || confess("Open error: $history_log_filepath");
    flock($history_log_fh, 2) || confess("Lock error: $history_log_filepath");
    $self->{HISTORY_LOG_FH} = $history_log_fh;

    # ����ID���O�t�@�C�� JSON�ǂݍ���
    if (-s $history_log_filepath > 0) {
        my $json_file_contents = do {
            # �������O�t�@�C���̏ꍇ
            seek($history_log_fh, 0, 0);
            local $/;
            <$history_log_fh>
        };
        Encode::decode('UTF-8', $json_file_contents);
        $self = { %{$json->utf8(1)->decode($json_file_contents)}, %{$self} };
    }

    # �N���[�W����`
    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }
        if (@_) {
            # 1�ȏ�̈������^����ꂽ�ꍇ
            my $field = shift;
            if (@_) {
                # 2�̈������^����ꂽ�̂ŁA�l���Z�b�g/�폜����
                my $value = shift;
                if (defined($value)) {
                    # �l���Z�b�g
                    $self->{$field} = $value;
                } else {
                    # �Z�b�g����l���Ȃ��̂ŁA�L�[���ƍ폜
                    delete($self->{$field});
                }
                # �ۑ����s��Ȃ��t���O�������Ă���ꍇ�������A
                # ����ID���O�t�@�C���ɕۑ�
                my $dont_perform_save = shift;
                if (!defined($dont_perform_save) || !$dont_perform_save) {
                    # ����ID���O�t�@�C�� JSON��������
                    my %save_hash = %{$self};
                    delete($save_hash{HISTORY_LOG_FH});
                    seek($history_log_fh, 0, 0);
                    truncate($history_log_fh, 0);
                    print $history_log_fh $json->utf8(1)->encode(\%save_hash);
                }
            }
            # �L�[�ɑΉ�����l��Ԃ�
            if (exists($self->{$field})) {
                return $self->{$field};
            } else {
                return;
            }
        }
    };

    return bless $closure, $class;
}

sub DESTROY {
    my $self = shift;

    # �������O�t�@�C���n���h�� �N���[�Y
    my $history_log_fh = $self->('HISTORY_LOG_FH');
    close($history_log_fh);
}

sub add_post_history {
    my ($self, $thread_no, $res_no, $time) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # �����̏������ݗ������O�ŁA�X���b�h���O�����݂���X���b�h�݂̂ƂȂ�悤�t�B���^�����O
    # (��ɕۑ�����̂ŁA�������O�t�@�C���ւ̏������݂͍s��Ȃ�)
    $validate_post_histories->($self, 1);

    # �������ݗ������O���擾
    my @post_history;
    if (defined(my $post_histories_array_ref = $self->('PostHistory'))) {
        # �ǉ�����X���b�h�ԍ��Ɠ����X���b�h�ԍ��̗����������āA���O���擾
        @post_history = grep { ${$_}[0] != $thread_no } @{$post_histories_array_ref};
    }

    # �������ݗ������O�z��擪�ɏ������݃X���b�h����ǉ����A
    # �����L�^������𒴂����ꍇ�ɌÂ��������폜
    unshift(@post_history, [$thread_no, $res_no, int($time)]);
    if ((my $history_delete_element_count = (scalar(@post_history) - $main::history_save_max)) > 0) {
        splice(@post_history, $main::history_save_max, $history_delete_element_count);
    }
    if (scalar(@post_history) > 0) {
        # �������ݗ������O���A�b�v�f�[�g
        $self->('PostHistory', \@post_history);
    } else {
        # �������ݗ������O��1�����Ȃ��̂ŁA�L�[���ƍ폜
        $self->('PostHistory', undef);
    }
}

sub get_post_histories {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # �����̏������ݗ������O�ŁA�X���b�h���O�����݂���X���b�h�݂̂ƂȂ�悤�t�B���^�����O
    $validate_post_histories->($self);

    if (defined(my $post_histories_array_ref = $self->('PostHistory'))) {
        # �z�񃊃t�@�����X��Ԃ�
        return $post_histories_array_ref;
    } else {
        # �������ݗ������O�ɋL�^����Ă��Ȃ��ꍇ�́A
        # ��z��̔z�񃊃t�@�����X��Ԃ�
        return [];
    }
}
sub delete_post_histories {
    my ($self, $delete_thread_no_array_ref) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # �����̏������ݗ������O�ŁA�X���b�h���O�����݂���X���b�h�݂̂ƂȂ�悤�t�B���^�����O
    $validate_post_histories->($self);

    # �������ݗ������O���擾���A�폜����X���b�h�ԍ��Ɠ����X���b�h�ԍ��̗���������
    my @post_history;
    if (defined(my $post_histories_array_ref = $self->('PostHistory'))) {
        @post_history = grep {
            my $exist_thread_no = ${$_}[0];
            scalar(grep { $_ == $exist_thread_no } @{$delete_thread_no_array_ref}) == 0
        } @{$post_histories_array_ref};
    }

    if (scalar(@post_history) > 0) {
        # �������ݗ������O���A�b�v�f�[�g
        $self->('PostHistory', \@post_history);
    } else {
        # �������ݗ������O��1�����Ȃ��̂ŁA�L�[���ƍ폜
        $self->('PostHistory', undef);
    }
}

sub get_ngthread_settings {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $ngthread_settings_hash_ref = $self->('NGThread'))) {
        # �n�b�V�����t�@�����X��Ԃ�
        return $ngthread_settings_hash_ref;
    } else {
        # �ݒ肪�L�^����Ă��Ȃ��ꍇ�́A
        # �l�������Z�b�g����Ă��Ȃ��n�b�V�����t�@�����X��Ԃ�
        return {};
    }
}

sub set_ngthread_settings {
    my ($self, $ngthread_settings_hash_ref) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($ngthread_settings_hash_ref)) {
        # NGThread.pm��save�T�u���[�`�����ō쐬�����
        # NG�X���b�h�֘A�ݒ�̃n�b�V�����t�@�����X�����̂܂ܒl�Ƃ��ĕۑ�����
        $self->('NGThread', $ngthread_settings_hash_ref);
    } else {
        # �ݒ肪�n����Ȃ��������߁A�L�[���ƍ폜
        $self->('NGThread', undef);
    }
}

sub get_ngid_settings {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $ngid_settings_array_ref = $self->('NGID_LIST'))) {
        # �z�񃊃t�@�����X��Ԃ�
        return $ngid_settings_array_ref;
    } else {
        # �ݒ肪�L�^����Ă��Ȃ��ꍇ�́A
        # ��z��̔z�񃊃t�@�����X��Ԃ�
        return [];
    }
}

sub set_ngid_settings {
    my ($self, $ngid_settings_array_ref) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }
    if (defined($ngid_settings_array_ref) && scalar(@{$ngid_settings_array_ref}) > 0) {
        # �����Ƃ��ēn���ꂽ�ANGID�ݒ�z�񃊃t�@�����X�����̂܂ܒl�Ƃ��ĕۑ�����
        $self->('NGID_LIST', $ngid_settings_array_ref);
    } else {
        # �ݒ肪�n����Ȃ��������A�v�f����0�̂��߁A�L�[���ƍ폜
        $self->('NGID_LIST', undef);
    }
}

sub get_ngname_settings {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $ngname_settings_hash_ref = $self->('NGNAME_LIST'))) {
        # �n�b�V�����t�@�����X��Ԃ�
        return $ngname_settings_hash_ref;
    } else {
        # �ݒ肪�L�^����Ă��Ȃ��ꍇ�́A
        # ��z��̃n�b�V�����t�@�����X��Ԃ�
        return {
            name => [],
            trip => []
        };
    }
}

sub set_ngname_settings {
    my ($self, $ngname_settings_hash_ref) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # ��z��̏ꍇ�ɃL�[���n���Ă��Ȃ��ꍇ�����邽�߁A
    # ��z��ō\�������n�b�V�����쐬���Ă���㏑������
    my %save_hash = (
        name => [],
        trip => []
    );
    if (defined($ngname_settings_hash_ref)) {
        foreach my $key ('name', 'trip') {
            if (exists(${$ngname_settings_hash_ref}{$key}) && ref(${$ngname_settings_hash_ref}{$key}) eq 'ARRAY') {
                $save_hash{$key} = ${$ngname_settings_hash_ref}{$key};
            }
        }
    }

    if (scalar(@{$save_hash{name}}) > 0 || scalar(@{$save_hash{trip}}) > 0) {
        # �����Ƃ��ēn���ꂽ�ANG�l�[���ݒ�n�b�V�����t�@�����X�����̂܂ܒl�Ƃ��ĕۑ�����
        $self->('NGNAME_LIST', \%save_hash);
    } else {
        # �ݒ肪�n����Ȃ��������A�v�f����0�̂��߁A�L�[���ƍ폜
        $self->('NGNAME_LIST', undef);
    }
}

sub get_ngword_settings {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $ngword_settings_array_ref = $self->('NGWORD_LIST'))) {
        # �z�񃊃t�@�����X��Ԃ�
        return $ngword_settings_array_ref;
    } else {
        # �ݒ肪�L�^����Ă��Ȃ��ꍇ�́A
        # ��z��̔z�񃊃t�@�����X��Ԃ�
        return [];
    }
}

sub set_ngword_settings {
    my ($self, $ngword_settings_array_ref) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }
    if (defined($ngword_settings_array_ref) && scalar(@{$ngword_settings_array_ref}) > 0) {
        # �����Ƃ��ēn���ꂽ�ANG���[�h�ݒ�z�񃊃t�@�����X�����̂܂ܒl�Ƃ��ĕۑ�����
        $self->('NGWORD_LIST', $ngword_settings_array_ref);
    } else {
        # �ݒ肪�n����Ȃ��������A�v�f����0�̂��߁A�L�[���ƍ폜
        $self->('NGWORD_LIST', undef);
    }
}

sub get_chain_ng_setting {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $chain_ng_flg = $self->('CHAIN_NG'))) {
        # �ۑ�����Ă���t���O�����̂܂ܕԂ�
        return $chain_ng_flg;
    } else {
        # �ݒ肪�L�^����Ă��Ȃ��ꍇ�́A
        # �f�t�H���g�ݒ�l��Ԃ�
        return $main::chain_ng;
    }
}

sub set_chain_ng_setting {
    my ($self, $flg) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # �t���O��1/0�ɕϊ����ĕۑ�
    $self->('CHAIN_NG', ($flg ? 1 : 0));
}

sub get_highlight_name_active_flag {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $highlight_name_flg = $self->('HIGHLIGHT_NAME'))) {
        # �ۑ�����Ă���t���O�����̂܂ܕԂ�
        return $highlight_name_flg;
    } else {
        # �ݒ肪�L�^����Ă��Ȃ��ꍇ��-1��Ԃ�
        return -1;
    }
}

sub set_highlight_name_active_flag {
    my ($self, $flg) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # �t���O��1/0�ɕϊ����ĕۑ�
    $self->('HIGHLIGHT_NAME', ($flg ? 1 : 0));
}

sub get_read_ng_settings {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    return {
        NGID_LIST => get_ngid_settings($self),
        NGNAME_LIST => get_ngname_settings($self),
        NGWORD_LIST => get_ngword_settings($self),
        CHAIN_NG => get_chain_ng_setting($self)
    };
}

=pod

=encoding cp932

=head1 NAME
HistoryLog - WebPatio ����ID���O���W���[��

=head1 SYNOPSIS
use HistoryLog;

# ����ID���O�ǂݍ���
$history_log = HistoryLog->new($history_id);

# NG�X���b�h�ݒ��ǉ����ĕۑ�
$history_log->add_post_history($thread_no, $res_no, $time);

# NG�X���b�h�ݒ���擾
my $ng_thread_settings_hash_ref = $history_log->get_post_histories();

# ����ID���O �C���X�^���X���̃��O�t�@�C���n���h�������
$history_log->DESTROY();

=head1 INTERFACE

=head2 Package Subroutines

=head3 C<< HistoryLog->new($history_id :Str) :HistoryLog >>

=over

=item I<$history_id :Str>
����ID���w�肵�A�C���X�^���X���쐬���܂�

����ID���O�t�@�C�����I�[�v���ł��Ȃ������b�N�ł��Ȃ��ꍇ�ɁA
L<Carp/confess>�ɂ��G���[�I�����܂�

=back

=head2 Instance Subroutines

=head3 C<< $history_log->DESTROY() >>
�C���X�^���X���̃��O�t�@�C���n���h����������邽�߁A
�C���X�^���X�̗��p���I������ꍇ�A�K�����̃T�u���[�`�����Ă�ŉ������B

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�

=head3 C<< $history_log->add_post_history([$thread_no :Int, $res_no :Int, $time :Int]) >>
�X���b�h�ԍ��A���X�ԍ��A�������ݎ�����Unixtime�������Ɏw�肵�āA
�������ݗ������O�ɒǉ����ĕۑ����܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->get_post_histories() :Ref<Array> >>
�������ݗ������O�ɕۑ�����Ă��鏑�����ݗ������O��
�������ݎ������V�������̔z�񃊃t�@�����X�ŕԂ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->delete_post_histories($delete_thread_no_array_ref :Ref<Array>) >>
��������폜����X���b�h�ԍ��̔z�񃊃t�@�����X�������Ɏw�肵�āA
�������ݗ������O����폜���ĕۑ����܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->get_ngthread_settings() :Ref<Hash> >>
����ID���O�t�@�C���ɕۑ�����Ă���NG�X���b�h�֘A�ݒ��
�n�b�V�����t�@�����X�ŕԂ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->set_ngthread_settings($ngthread_settings_hash_ref :Ref<Hash>) >>
�ݒ肷��NG�X���b�h�֘A�ݒ�̃n�b�V�����t�@�����X�������Ɏw�肵�āA
����ID���O�t�@�C���ɕۑ����܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->get_ngid_settings() :Ref<Array> >>
����ID���O�t�@�C���ɕۑ�����Ă���NGID�ݒ�̔z�񃊃t�@�����X��Ԃ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->set_ngid_settings($ngid_settings_array_ref :Ref<Array>) >>
NGID�ݒ�̔z�񃊃t�@�����X�������Ɏw�肵�āA
����ID���O�t�@�C���ɕۑ����܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->get_ngname_settings() :Ref<Hash> >>
����ID���O�t�@�C���ɕۑ�����Ă���NG�l�[���ݒ�̃n�b�V�����t�@�����X��Ԃ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->set_ngname_settings($ngname_settings_hash_ref :Ref<Hash>) >>
NG�l�[���ݒ�̃n�b�V�����t�@�����X�������Ɏw�肵�āA
����ID���O�t�@�C���ɕۑ����܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->get_ngword_settings() :Ref<Array> >>
����ID���O�t�@�C���ɕۑ�����Ă���NG���[�h�ݒ�̔z�񃊃t�@�����X��Ԃ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->set_ngword_settings($ngword_settings_array_ref :Ref<Array>) >>
NG���[�h�ݒ�̔z�񃊃t�@�����X�������Ɏw�肵�āA
����ID���O�t�@�C���ɕۑ����܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->get_chain_ng_settings() :Int >>
����ID���O�t�@�C���ɕۑ�����Ă���A��NG�ݒ�̗L��/�����t���O��Ԃ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->set_chain_ng_setting($flg :Int) >>
�A��NG�ݒ�̗L��/�����t���O�������Ɏw�肵�āA
����ID���O�t�@�C���ɕۑ����܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->get_highlight_name_active_flag() :Int >>
����ID���O�t�@�C���ɕۑ�����Ă���
�����̓��e��ڗ�������@�\�̗L��/�����t���O��Ԃ��܂�

����ID���O�t�@�C���Ƀt���O���ۑ�����Ă��Ȃ��ꍇ�́A-1��Ԃ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->set_highlight_name_active_flag($flg :Int) >>
�����̓��e��ڗ�������@�\�̗L��/�����t���O�������Ɏw�肵�āA
����ID���O�t�@�C���ɕۑ����܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=head3 C<< $history_log->get_read_ng_settings() :Ref<Hash> >>
����ID���O�t�@�C���ɕۑ�����Ă���A
�X���b�h�\�����(read.cgi)�Ŏg�p����NG�ݒ���܂Ƃ߂�
�n�b�V���ŕԂ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�


=cut

1;
