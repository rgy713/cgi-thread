package HistoryLog;
use strict;
use Encode;
use File::Spec;
use JSON::XS;

# 既存の書き込み履歴ログで、スレッドログが存在するスレッドのみとなるようフィルタリング
my $validate_post_histories = sub {
    my ($self, $dont_perform_save) = @_;

    if (defined(my $post_history_array_ref = $self->('PostHistory'))) {
        # フィルタリング実行前の要素数を取得
        my $before_validate_elements_count = scalar(@{$post_history_array_ref});

        # スレッドログファイルが存在しない要素は除外
        my @post_history = grep {
            my $log_thread_no = ${$_}[0];
            my $logfile_path = main::get_logfolder_path($log_thread_no) . "/$log_thread_no.cgi";
            -r $logfile_path;
        } @{$post_history_array_ref};

        # フィルタリング実行前後で要素数が変化した場合のみ、書き込み履歴ログをアップデート
        if (scalar(@post_history) != $before_validate_elements_count) {
            if (scalar(@post_history) > 0) {
                # 書き込み履歴ログをアップデート
                $self->('PostHistory', \@post_history, $dont_perform_save);
            } else {
                # 書き込み履歴ログが1件もないので、キーごと削除
                $self->('PostHistory', undef, $dont_perform_save);
            }
        }
    }
};

sub new {
    my ($class, $history_id) = @_;
    my $self = {};

    # JSON::XSインスタンス初期化
    my $json = JSON::XS->new();

    # 書込IDログファイルパス決定
    my $history_log_filepath = do {
        (my $folder_number = $history_id) =~ s/^([0-9]{2}).*/$1/;
        File::Spec->catfile($main::history_shared_conf{history_logdir}, $folder_number, "$history_id.log");
    };

    # 書込IDログファイルオープン
    open(my $history_log_fh, '+>>', $history_log_filepath) || confess("Open error: $history_log_filepath");
    flock($history_log_fh, 2) || confess("Lock error: $history_log_filepath");
    $self->{HISTORY_LOG_FH} = $history_log_fh;

    # 書込IDログファイル JSON読み込み
    if (-s $history_log_filepath > 0) {
        my $json_file_contents = do {
            # 既存ログファイルの場合
            seek($history_log_fh, 0, 0);
            local $/;
            <$history_log_fh>
        };
        Encode::decode('UTF-8', $json_file_contents);
        $self = { %{$json->utf8(1)->decode($json_file_contents)}, %{$self} };
    }

    # クロージャ定義
    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }
        if (@_) {
            # 1つ以上の引数が与えられた場合
            my $field = shift;
            if (@_) {
                # 2つの引数が与えられたので、値をセット/削除する
                my $value = shift;
                if (defined($value)) {
                    # 値をセット
                    $self->{$field} = $value;
                } else {
                    # セットする値がないので、キーごと削除
                    delete($self->{$field});
                }
                # 保存を行わないフラグが立っている場合を除き、
                # 書込IDログファイルに保存
                my $dont_perform_save = shift;
                if (!defined($dont_perform_save) || !$dont_perform_save) {
                    # 書込IDログファイル JSON書き込み
                    my %save_hash = %{$self};
                    delete($save_hash{HISTORY_LOG_FH});
                    seek($history_log_fh, 0, 0);
                    truncate($history_log_fh, 0);
                    print $history_log_fh $json->utf8(1)->encode(\%save_hash);
                }
            }
            # キーに対応する値を返す
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

    # 履歴ログファイルハンドラ クローズ
    my $history_log_fh = $self->('HISTORY_LOG_FH');
    close($history_log_fh);
}

sub add_post_history {
    my ($self, $thread_no, $res_no, $time) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # 既存の書き込み履歴ログで、スレッドログが存在するスレッドのみとなるようフィルタリング
    # (後に保存するので、履歴ログファイルへの書き込みは行わない)
    $validate_post_histories->($self, 1);

    # 書き込み履歴ログを取得
    my @post_history;
    if (defined(my $post_histories_array_ref = $self->('PostHistory'))) {
        # 追加するスレッド番号と同じスレッド番号の履歴を除いて、ログを取得
        @post_history = grep { ${$_}[0] != $thread_no } @{$post_histories_array_ref};
    }

    # 書き込み履歴ログ配列先頭に書き込みスレッド情報を追加し、
    # 履歴記録上限数を超えた場合に古い履歴を削除
    unshift(@post_history, [$thread_no, $res_no, int($time)]);
    if ((my $history_delete_element_count = (scalar(@post_history) - $main::history_save_max)) > 0) {
        splice(@post_history, $main::history_save_max, $history_delete_element_count);
    }
    if (scalar(@post_history) > 0) {
        # 書き込み履歴ログをアップデート
        $self->('PostHistory', \@post_history);
    } else {
        # 書き込み履歴ログが1件もないので、キーごと削除
        $self->('PostHistory', undef);
    }
}

sub get_post_histories {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # 既存の書き込み履歴ログで、スレッドログが存在するスレッドのみとなるようフィルタリング
    $validate_post_histories->($self);

    if (defined(my $post_histories_array_ref = $self->('PostHistory'))) {
        # 配列リファレンスを返す
        return $post_histories_array_ref;
    } else {
        # 書き込み履歴ログに記録されていない場合は、
        # 空配列の配列リファレンスを返す
        return [];
    }
}
sub delete_post_histories {
    my ($self, $delete_thread_no_array_ref) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # 既存の書き込み履歴ログで、スレッドログが存在するスレッドのみとなるようフィルタリング
    $validate_post_histories->($self);

    # 書き込み履歴ログを取得し、削除するスレッド番号と同じスレッド番号の履歴を除く
    my @post_history;
    if (defined(my $post_histories_array_ref = $self->('PostHistory'))) {
        @post_history = grep {
            my $exist_thread_no = ${$_}[0];
            scalar(grep { $_ == $exist_thread_no } @{$delete_thread_no_array_ref}) == 0
        } @{$post_histories_array_ref};
    }

    if (scalar(@post_history) > 0) {
        # 書き込み履歴ログをアップデート
        $self->('PostHistory', \@post_history);
    } else {
        # 書き込み履歴ログが1件もないので、キーごと削除
        $self->('PostHistory', undef);
    }
}

sub get_ngthread_settings {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $ngthread_settings_hash_ref = $self->('NGThread'))) {
        # ハッシュリファレンスを返す
        return $ngthread_settings_hash_ref;
    } else {
        # 設定が記録されていない場合は、
        # 値が何もセットされていないハッシュリファレンスを返す
        return {};
    }
}

sub set_ngthread_settings {
    my ($self, $ngthread_settings_hash_ref) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($ngthread_settings_hash_ref)) {
        # NGThread.pmのsaveサブルーチン内で作成される
        # NGスレッド関連設定のハッシュリファレンスをそのまま値として保存する
        $self->('NGThread', $ngthread_settings_hash_ref);
    } else {
        # 設定が渡されなかったため、キーごと削除
        $self->('NGThread', undef);
    }
}

sub get_ngid_settings {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $ngid_settings_array_ref = $self->('NGID_LIST'))) {
        # 配列リファレンスを返す
        return $ngid_settings_array_ref;
    } else {
        # 設定が記録されていない場合は、
        # 空配列の配列リファレンスを返す
        return [];
    }
}

sub set_ngid_settings {
    my ($self, $ngid_settings_array_ref) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }
    if (defined($ngid_settings_array_ref) && scalar(@{$ngid_settings_array_ref}) > 0) {
        # 引数として渡された、NGID設定配列リファレンスをそのまま値として保存する
        $self->('NGID_LIST', $ngid_settings_array_ref);
    } else {
        # 設定が渡されなかったか、要素数が0のため、キーごと削除
        $self->('NGID_LIST', undef);
    }
}

sub get_ngname_settings {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $ngname_settings_hash_ref = $self->('NGNAME_LIST'))) {
        # ハッシュリファレンスを返す
        return $ngname_settings_hash_ref;
    } else {
        # 設定が記録されていない場合は、
        # 空配列のハッシュリファレンスを返す
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

    # 空配列の場合にキーが渡ってこない場合があるため、
    # 空配列で構成されるハッシュを作成してから上書きする
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
        # 引数として渡された、NGネーム設定ハッシュリファレンスをそのまま値として保存する
        $self->('NGNAME_LIST', \%save_hash);
    } else {
        # 設定が渡されなかったか、要素数が0のため、キーごと削除
        $self->('NGNAME_LIST', undef);
    }
}

sub get_ngword_settings {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $ngword_settings_array_ref = $self->('NGWORD_LIST'))) {
        # 配列リファレンスを返す
        return $ngword_settings_array_ref;
    } else {
        # 設定が記録されていない場合は、
        # 空配列の配列リファレンスを返す
        return [];
    }
}

sub set_ngword_settings {
    my ($self, $ngword_settings_array_ref) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }
    if (defined($ngword_settings_array_ref) && scalar(@{$ngword_settings_array_ref}) > 0) {
        # 引数として渡された、NGワード設定配列リファレンスをそのまま値として保存する
        $self->('NGWORD_LIST', $ngword_settings_array_ref);
    } else {
        # 設定が渡されなかったか、要素数が0のため、キーごと削除
        $self->('NGWORD_LIST', undef);
    }
}

sub get_chain_ng_setting {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $chain_ng_flg = $self->('CHAIN_NG'))) {
        # 保存されているフラグをそのまま返す
        return $chain_ng_flg;
    } else {
        # 設定が記録されていない場合は、
        # デフォルト設定値を返す
        return $main::chain_ng;
    }
}

sub set_chain_ng_setting {
    my ($self, $flg) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # フラグを1/0に変換して保存
    $self->('CHAIN_NG', ($flg ? 1 : 0));
}

sub get_highlight_name_active_flag {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $highlight_name_flg = $self->('HIGHLIGHT_NAME'))) {
        # 保存されているフラグをそのまま返す
        return $highlight_name_flg;
    } else {
        # 設定が記録されていない場合は-1を返す
        return -1;
    }
}

sub set_highlight_name_active_flag {
    my ($self, $flg) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    # フラグを1/0に変換して保存
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
HistoryLog - WebPatio 書込IDログモジュール

=head1 SYNOPSIS
use HistoryLog;

# 書込IDログ読み込み
$history_log = HistoryLog->new($history_id);

# NGスレッド設定を追加して保存
$history_log->add_post_history($thread_no, $res_no, $time);

# NGスレッド設定を取得
my $ng_thread_settings_hash_ref = $history_log->get_post_histories();

# 書込IDログ インスタンス内のログファイルハンドルを解放
$history_log->DESTROY();

=head1 INTERFACE

=head2 Package Subroutines

=head3 C<< HistoryLog->new($history_id :Str) :HistoryLog >>

=over

=item I<$history_id :Str>
書込IDを指定し、インスタンスを作成します

書込IDログファイルをオープンできないかロックできない場合に、
L<Carp/confess>によりエラー終了します

=back

=head2 Instance Subroutines

=head3 C<< $history_log->DESTROY() >>
インスタンス内のログファイルハンドルを解放するため、
インスタンスの利用を終了する場合、必ずこのサブルーチンを呼んで下さい。

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します

=head3 C<< $history_log->add_post_history([$thread_no :Int, $res_no :Int, $time :Int]) >>
スレッド番号、レス番号、書き込み時刻のUnixtimeを引数に指定して、
書き込み履歴ログに追加して保存します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->get_post_histories() :Ref<Array> >>
書き込み履歴ログに保存されている書き込み履歴ログを
書き込み時刻が新しい順の配列リファレンスで返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->delete_post_histories($delete_thread_no_array_ref :Ref<Array>) >>
履歴から削除するスレッド番号の配列リファレンスを引数に指定して、
書き込み履歴ログから削除して保存します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->get_ngthread_settings() :Ref<Hash> >>
書込IDログファイルに保存されているNGスレッド関連設定を
ハッシュリファレンスで返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->set_ngthread_settings($ngthread_settings_hash_ref :Ref<Hash>) >>
設定するNGスレッド関連設定のハッシュリファレンスを引数に指定して、
書込IDログファイルに保存します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->get_ngid_settings() :Ref<Array> >>
書込IDログファイルに保存されているNGID設定の配列リファレンスを返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->set_ngid_settings($ngid_settings_array_ref :Ref<Array>) >>
NGID設定の配列リファレンスを引数に指定して、
書込IDログファイルに保存します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->get_ngname_settings() :Ref<Hash> >>
書込IDログファイルに保存されているNGネーム設定のハッシュリファレンスを返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->set_ngname_settings($ngname_settings_hash_ref :Ref<Hash>) >>
NGネーム設定のハッシュリファレンスを引数に指定して、
書込IDログファイルに保存します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->get_ngword_settings() :Ref<Array> >>
書込IDログファイルに保存されているNGワード設定の配列リファレンスを返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->set_ngword_settings($ngword_settings_array_ref :Ref<Array>) >>
NGワード設定の配列リファレンスを引数に指定して、
書込IDログファイルに保存します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->get_chain_ng_settings() :Int >>
書込IDログファイルに保存されている連鎖NG設定の有効/無効フラグを返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->set_chain_ng_setting($flg :Int) >>
連鎖NG設定の有効/無効フラグを引数に指定して、
書込IDログファイルに保存します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->get_highlight_name_active_flag() :Int >>
書込IDログファイルに保存されている
自分の投稿を目立たせる機能の有効/無効フラグを返します

書込IDログファイルにフラグが保存されていない場合は、-1を返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->set_highlight_name_active_flag($flg :Int) >>
自分の投稿を目立たせる機能の有効/無効フラグを引数に指定して、
書込IDログファイルに保存します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=head3 C<< $history_log->get_read_ng_settings() :Ref<Hash> >>
書込IDログファイルに保存されている、
スレッド表示画面(read.cgi)で使用するNG設定をまとめて
ハッシュで返します

HistoryCookieインスタンスの外からこのサブルーチンを呼ぶと、
L<Carp/confess>によりエラー終了します


=cut

1;
