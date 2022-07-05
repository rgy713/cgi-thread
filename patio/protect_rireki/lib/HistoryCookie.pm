package HistoryCookie;

use strict;
use Carp qw(carp confess);

use File::Basename;
use File::Spec;
require File::Spec->catfile(dirname(__FILE__), '..', 'init.cgi');
my %cf = init();

my $COOKIE_NAME = 'WEB_PATIO_HISTORY_ID';

#-----------------------------------------------------------
#  ���O�C���F��
#-----------------------------------------------------------
my $login_authenticate = sub {
    my ($history_id, $history_password) = @_;

    # �p�X�t�@�C���I�[�v��
    open(IN,"$cf{pwdfile}") or return;
    flock(IN, 1) or return;
    while (<IN>) {
        my ($id,$crypt,$hash) = split(/:/);
        if ($history_id eq $id) {
            # �p�X���[�h�ƍ�����
            if ($history_password ne decrypt($crypt)) {
                return;
            }
            # �F�ؐ���
            return $hash;
        }
    }
    close(IN);

    # ID��������Ȃ�
    return;
};

#-----------------------------------------------------------
#  �n�b�V�������[�U�[�F�؃n�b�V���F��
#  �F�؂ɐ��������ꍇ�A�����p�X���[�h���Ԃ�A���s�����ꍇ�͋󕶎����Ԃ�
#-----------------------------------------------------------
my $user_auth_hash_authenticate = sub {
    my ($history_id, $hashed_user_auth_hash) = @_;

    # �p�X�t�@�C���I�[�v��
    open(IN,"$cf{pwdfile}") or return;
    flock(IN, 1);
    while (<IN>) {
        my ($id, $crypt, $hash) = split(/:/);

        if ($id eq $history_id) {
            close(IN);
            # �F�؏�񃍃O�ɋL�^�����n�b�V�����X�Ƀn�b�V���������l��Cookie�ɋL�^���Ă���̂ŁA
            # verify�p�̃T�u���[�`���ʂ��ďƍ�����
            if (saltedhash_verify($hashed_user_auth_hash, $hash)) {
                return decrypt($crypt);
            } else {
                return;
            }
        }
    }
    close(IN);
    return;
};

#-----------------------------------------------------------
#  ����ID Cookie�Z�b�g
#-----------------------------------------------------------
my $cookie_value_set = sub {
    my ($issue_value) = @_;

    if (defined($issue_value)) {
        # ���s
        print "Set-Cookie: $COOKIE_NAME=$issue_value; expires=Tue, 19 Jan 2038 03:14:06 GMT; path=/\n";
    } else {
        # �폜
        print "Set-Cookie: $COOKIE_NAME=; expires=Thu, 1 Jan 1970 00:00:00 GMT; path=/\n";
    }
};

sub new {
    my $class = shift;
    my $self = {};

    # read cookie value
    foreach my $cookie_set (split(/; */, $ENV{'HTTP_COOKIE'})) {
        my ($key, $value) = split(/=/, $cookie_set);
        if ($key eq $COOKIE_NAME) {
            if ($value ne '') {
                my ($history_id, $hashed_auth_hash) = split(/-/, $value, 2);
                my $history_password = $user_auth_hash_authenticate->($history_id, $hashed_auth_hash); # �F�ؐ�������ƁA�����p�X���[�h���Ԃ�
                if ($history_password) {
                    # �F�ؐ������ɁA�C���X�^���X�ɏ���ID/�p�X���[�h���Z�b�g����
                    $self->{'HISTORY_ID'} = $history_id;
                    $self->{'HISTORY_PASSWORD'} = $history_password;
                } else {
                    # �F�؎��s���͋������O�A�E�g
                    $cookie_value_set->();
                }
            }
            last;
        }
    }

    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }
        my $field = shift;
        if (@_) {
            $self->{$field} = shift;
        }
        return $self->{$field};
    };

    return bless $closure, $class;
}

sub login {
    my ($self, $history_id, $history_password) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # �F��
    my $user_auth_hash = $login_authenticate->($history_id, $history_password);
    if (!$user_auth_hash) {
        return;
    }

    # Cookie�Z�b�g
    $cookie_value_set->("${history_id}-" . saltedhash_encrypt(${user_auth_hash}));

    # ���O�C������
    $self->('HISTORY_ID', $history_id);
    $self->('HISTORY_PASSWORD', $history_password);
    return 1;
}

sub logout {
    my ($self) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # Cookie�폜
    $cookie_value_set->();

    $self->('HISTORY_ID', undef);
    $self->('HISTORY_PASSWORD', undef);
}

sub get_history_id {
    my ($self) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    return $self->('HISTORY_ID');
}

sub change_user_hash {
    my ($self, $new_hashed_user_auth_hash) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if(!defined($self->('HISTORY_ID'))) {
        return;
    }

    # Cookie�Z�b�g
    $cookie_value_set->($self->('HISTORY_ID') . "-$new_hashed_user_auth_hash");

    return 1;
}

1;

=pod

=encoding cp932

=head1 NAME
HistoryCookie - WebPatio/WebProtect ����IDCookie��舵�����W���[��

=head1 SYNOPSIS
use HistoryCookie;

# �C���X�^���X������
$cookie = HistoryCookie->new();

=head1 INTERFACE

=head2 Package Subroutines

=head3 C<< HistoryCookie->new($cookieTypeConstant) :HistoryCookie >>

=over

=item I<$cookieTypeConstant>
�C���X�^���X���쐬���܂�

=back

=head2 Instance Subroutines

=head3 C<< $cookie->login([$history_id :Str, $history_password :Str]) :Int >>
���O�C�����s���A�F�؂ɐ��������ꍇ�́A����IDCookie�𔭍s����1��Ԃ��A
�F�؂Ɏ��s�����ꍇ��0��Ԃ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�

=head3 C<< $cookie->logout() >>
���O�C����Ԃɂ�����炸�A���O�A�E�g�����݂܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�

=head3 C<< $cookie->get_history_id() :Str >>
���O�C�����Ă���ꍇ�́A����ID��Ԃ��܂�
���O�C�����Ă��Ȃ��ꍇ�́Aundef��Ԃ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�

=head3 C<< $cookie->change_user_hash([$new_hashed_user_auth_hash :Str]) :Int >>
���O�C�����Ă���ꍇ�́A�V�����n�b�V����Cookie�ɃZ�b�g���A1��Ԃ��܂�
���O�C�����Ă��Ȃ��ꍇ�́Aundef��Ԃ��܂�

HistoryCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�

=cut
