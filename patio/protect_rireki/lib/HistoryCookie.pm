package HistoryCookie;

use strict;
use Carp qw(carp confess);

use File::Basename;
use File::Spec;
require File::Spec->catfile(dirname(__FILE__), '..', 'init.cgi');
my %cf = init();

my $COOKIE_NAME = 'WEB_PATIO_HISTORY_ID';

#-----------------------------------------------------------
#  ログイン認証
#-----------------------------------------------------------
my $login_authenticate = sub {
    my ($history_id, $history_password) = @_;

    # パスファイルオープン
    open(IN,"$cf{pwdfile}") or return;
    flock(IN, 1) or return;
    while (<IN>) {
        my ($id,$crypt,$hash) = split(/:/);
        if ($history_id eq $id) {
            # パスワード照合処理
            if ($history_password ne decrypt($crypt)) {
                return;
            }
            # 認証成功
            return $hash;
        }
    }
    close(IN);

    # IDが見つからない
    return;
};

#-----------------------------------------------------------
#  ハッシュ化ユーザー認証ハッシュ認証
#  認証に成功した場合、履歴パスワードが返り、失敗した場合は空文字が返る
#-----------------------------------------------------------
my $user_auth_hash_authenticate = sub {
    my ($history_id, $hashed_user_auth_hash) = @_;

    # パスファイルオープン
    open(IN,"$cf{pwdfile}") or return;
    flock(IN, 1);
    while (<IN>) {
        my ($id, $crypt, $hash) = split(/:/);

        if ($id eq $history_id) {
            close(IN);
            # 認証情報ログに記録したハッシュを更にハッシュ化した値をCookieに記録しているので、
            # verify用のサブルーチン通して照合する
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
#  書込ID Cookieセット
#-----------------------------------------------------------
my $cookie_value_set = sub {
    my ($issue_value) = @_;

    if (defined($issue_value)) {
        # 発行
        print "Set-Cookie: $COOKIE_NAME=$issue_value; expires=Tue, 19 Jan 2038 03:14:06 GMT; path=/\n";
    } else {
        # 削除
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
                my $history_password = $user_auth_hash_authenticate->($history_id, $hashed_auth_hash); # 認証成功すると、履歴パスワードが返る
                if ($history_password) {
                    # 認証成功時に、インスタンスに書込ID/パスワードをセットする
                    $self->{'HISTORY_ID'} = $history_id;
                    $self->{'HISTORY_PASSWORD'} = $history_password;
                } else {
                    # 認証失敗時は強制ログアウト
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

    # 認証
    my $user_auth_hash = $login_authenticate->($history_id, $history_password);
    if (!$user_auth_hash) {
        return;
    }

    # Cookieセット
    $cookie_value_set->("${history_id}-" . saltedhash_encrypt(${user_auth_hash}));

    # ログイン完了
    $self->('HISTORY_ID', $history_id);
    $self->('HISTORY_PASSWORD', $history_password);
    return 1;
}

sub logout {
    my ($self) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # Cookie削除
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

    # Cookieセット
    $cookie_value_set->($self->('HISTORY_ID') . "-$new_hashed_user_auth_hash");

    return 1;
}

1;

=pod

=encoding cp932

=head1 NAME
HistoryCookie - WebPatio/WebProtect 書込IDCookie取り扱いモジュール

=head1 SYNOPSIS
use HistoryCookie;

# インスタンス初期化
$cookie = HistoryCookie->new();

=head1 INTERFACE

=head2 Package Subroutines

=head3 C<< HistoryCookie->new($cookieTypeConstant) :HistoryCookie >>

=over

=item I<$cookieTypeConstant>
インスタンスを作成します

=back

=head2 Instance Subroutines

=head3 C<< $cookie->login([$history_id :Str, $history_password :Str]) :Int >>
ログインを行い、認証に成功した場合は、書込IDCookieを発行して1を返し、
認証に失敗した場合は0を返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します

=head3 C<< $cookie->logout() >>
ログイン状態にかかわらず、ログアウトを試みます

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します

=head3 C<< $cookie->get_history_id() :Str >>
ログインしている場合は、書込IDを返します
ログインしていない場合は、undefを返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します

=head3 C<< $cookie->change_user_hash([$new_hashed_user_auth_hash :Str]) :Int >>
ログインしている場合は、新しいハッシュをCookieにセットし、1を返します
ログインしていない場合は、undefを返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します

=cut
