package UniqueCookie;

use strict;
use Carp qw(carp confess);

sub new {
    my $class = shift;
    if (scalar(@_) < 1) {
        confess('The first argument must be set as part of cookie name.');
    }

    my $self = { NAME  => "WEB_PATIO_$_[0]_UQ_A" };
    $self->{'VALUE'} = do {
        # read cookie value (don't issue)
        my $cookie_value;
        foreach my $cookie_set (split(/; */, $ENV{'HTTP_COOKIE'})) {
            my ($key, $value) = split(/=/, $cookie_set);
            if ($key eq $self->{'NAME'}) {
                if ($value ne '') {
                    $cookie_value = $value;
                }
                last;
            }
        }
        $cookie_value;
    };

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

sub value {
    my ($self, $is_issue_cookie, $import_value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # issue cookie
    if (!$self->is_issued() && $is_issue_cookie) {
        my $issue_value = do {
            if ($import_value) {
                # import value
                $import_value;
            } else {
                # create new value
                my ($min,$hour,$mday,$mon,$year) = @main::localtime[1..5];
                $year = substr($year + 1900, -2);
                $mon = $mon + 1;

                if ($main::idcrypt eq '') {
                    main::makeid();
                }
                my $patio_id = substr($main::idcrypt, 0, 2);
                #$patio_id =~ tr/\/,/ab/;
                #.��C�ɕϊ�
                $patio_id =~ tr/\/,\./abc/;

                sprintf("%02d%02d%02d_%s_%02d%02d", $year, $mon, $mday, $patio_id, $hour, $min);
            }
        };
        if (length($issue_value) <= 4093) {
            print 'Set-Cookie: ' . $self->('NAME') . "=$issue_value; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
            $self->('VALUE', $issue_value);
        } else {
            carp('Cookie value size limit exceeded. Can\'t set.');
        }
    }

    return $self->('VALUE');
}

sub is_issued {
    my ($self) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }
    return defined($self->('VALUE'));
}

1;

=pod

=encoding cp932

=head1 NAME
UniqueCookie - WebPatio ���j�[�NCookieA��舵�����W���[��

=head1 SYNOPSIS
use UniqueCookie;

# CookieA�̓ǂݍ���
$cookie_a = UniqueCookie->new();

# CookieA�ɃZ�b�g����Ă���l��Ԃ�(�Ȃ��ꍇ��undef)
my $ret_a = $cookie_a->value();

# CookieA�𔭍s���Ă��̒l��Ԃ� (���łɑ��݂���ꍇ�͔��s�����ɃZ�b�g����Ă���l��Ԃ�)
my $ret_b = $cookie_a->value(1);

# CookieA���w�肵���l�Ŕ��s���Ă��̒l��Ԃ� (���łɑ��݂���ꍇ�͔��s�����ɃZ�b�g����Ă���l��Ԃ�)
my $ret_c = $cookie_a->value(1, "hogehoge");

# CookieA�͔��s�ς��ǂ������擾
my $is_cookie_a_issued = $cookie_a->is_issued();

=head1 INTERFACE

=head2 Package Subroutines

=head3 C<< UniqueCookie->new() :UniqueCookie >>

=head2 Instance Subroutines

=head3 C<< $cookie->value([$issue_cookie :Int, $issue_cookie_value :Str]) :Str >>
�����������w�肵�Ȃ��ŌĂ񂾏ꍇ�ACookie�ɃZ�b�g����Ă���l��Ԃ��܂�

UniqueCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�

=over

=item I<$cookieTypeConstant>
1�ȏ�̐��l���Z�b�g���ČĂ񂾏ꍇ�A
Cookie�ɒl���Z�b�g����Ă��Ȃ���΁A�����I�ɒl���Z�b�g����Cookie�𔭍s���A���̒l��Ԃ��܂�

=item I<$issue_cookie_value>
�����񂪃Z�b�g����Ă���ꍇ�A
Cookie�ɒl���Z�b�g����Ă��Ȃ���΁A���̒l���Z�b�g����Cookie�𔭍s���A���̒l��Ԃ��܂�

=back

=head3 C<< $cookie->is_issued() :Int >>
Cookie�����s�ς��ǂ�����Ԃ��܂�

UniqueCookie�C���X�^���X�̊O���炱�̃T�u���[�`�����ĂԂƁA
L<Carp/confess>�ɂ��G���[�I�����܂�

=cut
