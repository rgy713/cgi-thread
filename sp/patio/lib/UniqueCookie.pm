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
                #.もCに変換
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
UniqueCookie - WebPatio ユニークCookieA取り扱いモジュール

=head1 SYNOPSIS
use UniqueCookie;

# CookieAの読み込み
$cookie_a = UniqueCookie->new();

# CookieAにセットされている値を返す(ない場合はundef)
my $ret_a = $cookie_a->value();

# CookieAを発行してその値を返す (すでに存在する場合は発行せずにセットされている値を返す)
my $ret_b = $cookie_a->value(1);

# CookieAを指定した値で発行してその値を返す (すでに存在する場合は発行せずにセットされている値を返す)
my $ret_c = $cookie_a->value(1, "hogehoge");

# CookieAは発行済かどうかを取得
my $is_cookie_a_issued = $cookie_a->is_issued();

=head1 INTERFACE

=head2 Package Subroutines

=head3 C<< UniqueCookie->new() :UniqueCookie >>

=head2 Instance Subroutines

=head3 C<< $cookie->value([$issue_cookie :Int, $issue_cookie_value :Str]) :Str >>
何も引数を指定しないで呼んだ場合、Cookieにセットされている値を返します

UniqueCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します

=over

=item I<$cookieTypeConstant>
1以上の数値をセットして呼んだ場合、
Cookieに値がセットされていなければ、自動的に値をセットしてCookieを発行し、その値を返します

=item I<$issue_cookie_value>
文字列がセットされている場合、
Cookieに値がセットされていなければ、その値をセットしてCookieを発行し、その値を返します

=back

=head3 C<< $cookie->is_issued() :Int >>
Cookieが発行済かどうかを返します

UniqueCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します

=cut
