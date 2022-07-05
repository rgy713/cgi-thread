package NGThread;
use strict;
use JSON::XS;
use Encode qw();

use constant {
    DisplayMode_Hide => 0,
    DisplayMode_Replace => 1,
};

my @SETTINGS_KEYS = ('DisplayMode', 'ThreadCreator', 'ThreadTitle', 'ThreadTitleExclude');

# エスケープしたコンパイル済み正規表現を返す
my $regex_quote_compile = sub {
    my $quoted_word = quotemeta($_[0]);
    return qr/$quoted_word/;
};

my $IN_BRACKET_WORD_SEPARATER = '|';

my $AND_SEPARATE_REGEX = qr/_/;
my $META_SPLIT_REGEX = qr/(\[[^\[\]]*\])/;
my $BRACKET_CAPTURE_REGEX = qr/^\[([^\[\]]*)\]$/;
my $IN_BRACKET_WORD_SEPARATE_REGEX = $regex_quote_compile->($IN_BRACKET_WORD_SEPARATER);
my $LINE_BREAK_REGEX = qr/\r\n|\n|\r/;

my %compiled_regex_hash;

# 文字列が設定にマッチするかどうか
my $is_str_match_to_setting = sub {
    my ($str, $settings, $must_include_strings_array_ref) = @_;

    # 内部エンコードに変換
    my $utf8flagged_str = $main::enc_cp932->decode($str);
    my $utf8flagged_settings = Encode::is_utf8($settings) ? $settings : $main::enc_cp932->decode($settings);

    # 検査対象文字列から、設定文字列に含むべき文字列のリストを作成
    my @must_include_strings = do {
        my @tmp = ();
        if (defined($must_include_strings_array_ref) && ref($must_include_strings_array_ref) eq 'ARRAY') {
            foreach my $include_string (@{$must_include_strings_array_ref}) {
                my $utf8flagged_include_string = Encode::is_utf8($include_string) ? $include_string : $main::enc_cp932->decode($include_string);
                if (index($utf8flagged_str, $utf8flagged_include_string) >= 0) {
                    push(@tmp, $utf8flagged_include_string);
                }
            }
        }
        @tmp;
    };

    # 設定1行毎に判定
    LINE_LOOP: foreach my $line (grep { $_ ne '' } split($LINE_BREAK_REGEX, $utf8flagged_settings)) {
        # 設定文字列に含むべき文字が全て含まれているかどうかチェック
        if (grep { index($line, $_) == -1 } @must_include_strings) {
            next; # 含まれていない文字列が1つ以上見つかった時は、NG扱いしないためスキップ
        }

        # AND条件「_」分割
        my @and_set;
        push(@and_set, grep { $_ ne '' } split($AND_SEPARATE_REGEX, $line));

        # 空条件時はスキップ
        if (scalar(@and_set) == 0) {
            next;
        }

        # 重複条件をカウントしつつ、ユニーク化する
        my %exp_count;
        @and_set = grep(!$exp_count{$_}++, @and_set);

        # 正規表現による判定を行うかどうか (重複条件があるか、もしくは、メタ文字を含んでいるか)
        if (scalar(grep { $_ > 1 } values(%exp_count)) || scalar(grep { $_ =~ $META_SPLIT_REGEX } @and_set) > 0) {
            # 正規表現による部分一致判定
            # AND条件ごとに判定実施
            foreach my $and_keyword (@and_set) {
                # 正規表現をまだコンパイルしていない条件の場合はパターンを作成して、コンパイルを行う
                if (!exists($compiled_regex_hash{$and_keyword}) || !exists($compiled_regex_hash{$and_keyword}{$exp_count{$and_keyword}})) {
                    my $regex_str = '';
                    # メタ文字([])で分割
                    foreach my $meta_splited_keyword (grep { $_ ne '' } split($META_SPLIT_REGEX, $and_keyword)) {
                        if ($meta_splited_keyword =~ $BRACKET_CAPTURE_REGEX) {
                            # []のマッチ
                            # 文字一致判定のため、文字クラス正規表現を作成してハッシュに格納
                            if (index($1, $IN_BRACKET_WORD_SEPARATER) == -1) {
                                # 文字一致判定のため、文字クラス正規表現を作成してハッシュに格納
                                # 正規表現を使用するため、各文字をエスケープ
                                $regex_str .= '[' . quotemeta($1) . ']';
                            } else {
                                # |による単語分割OR判定
                                my @word_or_regex_str_array;
                                foreach my $word (grep { $_ ne '' } split($IN_BRACKET_WORD_SEPARATE_REGEX, $1)) {
                                    push(@word_or_regex_str_array, quotemeta($word)); # 正規表現を使用するため、各文字をエスケープ
                                }
                                $regex_str .= '(?:' . join('|', @word_or_regex_str_array) . ')'; # パターンを生成
                            }
                        } else {
                            # それ以外の通常文字列
                            $regex_str .= quotemeta($meta_splited_keyword);
                        }
                    }
                    if ($regex_str ne '') {
                        # 条件出現回数によって作成する正規表現を変える
                        if ($exp_count{$and_keyword} == 1) {
                            $compiled_regex_hash{$and_keyword}{1} = qr/$regex_str/;
                        } else {
                            # 条件に出現回数指定(n回以上)があるため、それを加えて正規表現を作成
                            $compiled_regex_hash{$and_keyword}{$exp_count{$and_keyword}} = qr/(?:.*?$regex_str.*?){$exp_count{$and_keyword},}/;
                        }
                    } else {
                        $compiled_regex_hash{$and_keyword} = undef;
                    }
                }

                # 判定実施
                if ($utf8flagged_str !~ $compiled_regex_hash{$and_keyword}{$exp_count{$and_keyword}}) {
                    # 不一致時は次の設定行判定へ
                    next LINE_LOOP;
                }
            }
            # 設定行のすべてに合致した
            return 1;
        } else {
            # 通常の部分一致による判定
            # AND条件ごとに判定実施
            foreach my $and_keyword (@and_set) {
                if (index($utf8flagged_str, $and_keyword) == -1) {
                    # 不一致時は次の設定行判定へ
                    next LINE_LOOP;
                }
            }
            # 設定行のすべてに合致した
            return 1;
        }
    }

    # いずれの設定行にも一致しなかった
    return 0;
};

sub new {
    my ($class, $history_log) = @_;
    my $self = {};

    # 設定読み込み
    my $load_values;
    if (defined($history_log)) {
        $self->{HISTORY_LOG} = $history_log;
        # 書込IDログから設定読み込み
        $load_values = $history_log->get_ngthread_settings();
    } else {
        # Cookieから設定読み込み
        $self->{NAME} = "WEB_PATIO_${main::cookie_current_dirpath}_NGThread";
        foreach my $cookie_set (split(/; */, $ENV{'HTTP_COOKIE'})) {
            my ($key, $value) = split(/=/, $cookie_set);
            if ($key eq $self->{'NAME'}) {
                if ($value ne '') {
                    my $urldecoded_value = $value;
                    $urldecoded_value =~ s/\+/ /g;
                    $urldecoded_value =~ s/%([0-9a-fA-F]{2})/pack("H2",$1)/eg;
                    $urldecoded_value = Encode::decode('UTF-8', $urldecoded_value);
                    $load_values = JSON::XS->new()->utf8(0)->decode($urldecoded_value);
                }
                last;
            }
        }
    }
    if (defined($load_values)) {
        # 読み込んだ設定値が定義されている時、
        # 必要に応じて内部エンコードをCP932に変換し、
        # 設定値として使用する
        foreach my $setting_key (@SETTINGS_KEYS) {
            if (exists(${$load_values}{$setting_key}) && ${$load_values}{$setting_key} ne '') {
                if (Encode::is_utf8(${$load_values}{$setting_key})) {
                    $self->{$setting_key} = $main::enc_cp932->encode(${$load_values}{$setting_key});
                } else {
                    $self->{$setting_key} = ${$load_values}{$setting_key};
                }
            }
        }
        $self = { %{$load_values}, %{$self} };
    }

    my $closure = sub {
        if ((caller)[0] ne (caller(0))[0]) {
            confess('call me only in instance subroutine.');
        }
        my $field = shift;
        if (@_) {
            $self->{$field} = shift;
        }
        if (exists($self->{$field})) {
            return $self->{$field};
        } else {
            return;
        }
    };

    return bless $closure, $class;
}

sub DESTROY {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined(my $history_log = $self->('HISTORY_LOG'))) {
        $history_log->DESTROY();
    }
}

sub get_display_mode {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($self->('DisplayMode'))) {
        if ($self->('DisplayMode') >= 0) {
            return $self->('DisplayMode');
        } else {
            # 0未満がセットされている時はデフォルト値を使用する
            return $main::ngthread_default_display_mode;
        }
    } else {
        return $main::ngthread_default_display_mode;
    }
}

sub set_display_mode {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }
    if ($value != DisplayMode_Hide && $value != DisplayMode_Replace) {
        confess('setting display mode is not valid.');
    }

    $self->('DisplayMode', int($value));
}

sub get_ng_thread_creator {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($self->('ThreadCreator'))) {
        return $self->('ThreadCreator');
    } else {
        return '';
    }
}

sub set_ng_thread_creator {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    $self->('ThreadCreator', $value);
}

sub get_ng_thread_title {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($self->('ThreadTitle'))) {
        return $self->('ThreadTitle');
    } else {
        return '';
    }
}

sub set_ng_thread_title {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    $self->('ThreadTitle', $value);
}

sub get_ng_thread_title_exclude {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (defined($self->('ThreadTitleExclude'))) {
        return $self->('ThreadTitleExclude');
    } else {
        return '';
    }
}

sub set_ng_thread_title_exclude {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    $self->('ThreadTitleExclude', $value);
}

sub is_ng_thread_creator {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (!defined($self->('ThreadCreator'))) {
        return 0;
    }

    return $is_str_match_to_setting->($value, $self->get_ng_thread_creator(), \@main::ngthread_thread_creator_must_include_strings);
}

sub is_ng_thread_title {
    my ($self, $value) = @_;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    if (!defined($self->('ThreadTitle'))) {
        return 0;
    }

    return $is_str_match_to_setting->($value, $self->get_ng_thread_title())
        && !$is_str_match_to_setting->($value, $self->get_ng_thread_title_exclude());
}

sub save {
    my $self = shift;
    if (!$self) {
        confess('call me only in instance variable.');
    }

    my %save_values;
    foreach my $key (@SETTINGS_KEYS) {
        if (defined($self->($key)) && $self->($key) ne '') {
            if ($key eq 'DisplayMode') {
                $save_values{$key} = int($self->($key));
            } else {
                $save_values{$key} = $main::enc_cp932->decode($self->($key));
            }
        }
    }
    if (!defined($self->('DisplayMode'))) {
        # DisplayModeの設定がない場合でも、領域を確保してデフォルト値であることを記録する
        # (後に規定バイト数超過で設定できなくなってしまうことを防ぐため)
        $save_values{'DisplayMode'} = -1;
    }

    if (defined(my $history_log = $self->('HISTORY_LOG'))) {
        # 書込IDログファイルに保存
        $history_log->set_ngthread_settings(\%save_values);
    } else {
        # Cookie保存のため、JSONにしてURLエンコード
        my $urlencoded_json_settings = JSON::XS->new->utf8(1)->encode(\%save_values);
        $urlencoded_json_settings =~ s/(\W)/'%' . unpack('H2', $1)/eg;
        $urlencoded_json_settings =~ s/\s/+/g;

        # Cookieサイズ判定・セット
        if(length($self->('NAME') . $urlencoded_json_settings) > 4093) {
            main::error('文字数オーバーです。', $main::bbscgi);
        } else {
            print 'Set-Cookie: ' . $self->('NAME') . "=$urlencoded_json_settings; expires=Tue, 19 Jan 2038 03:14:06 GMT\n";
        }
    }
}

1;

=pod

=encoding cp932

=head1 NAME
NGThread - WebPatio NGスレッドモジュール

=head1 SYNOPSIS
use NGThread;

# 書込IDログから設定の読み込み
# (引数に与える$history_logはHistoryLogモジュールのインスタンス)
$ngthread = NGThread->new($history_log);

# Cookieから設定の読み込み
$ngthread = NGThread->new();

# NGスレッド表示設定の取得
$ngthread->get_display_mode();

# NGスレッド表示設定のセット
$ngthread->set_display_mode(NGThread::DisplayMode_Hide);    # スレッド非表示にセット
$ngthread->set_display_mode(NGThread::DisplayMode_Replace); # スレッド名置換にセット

# スレッド作成者のNG設定を取得
my $value = $ngthread->get_ng_thread_creator();

# スレッド作成者のNG設定をセット
$ngthread->set_ng_thread_creator($value);

# スレッド名のNG設定を取得
my $value = $ngthread->get_ng_thread_title();

# スレッド名のNG設定をセット
$ngthread->set_ng_thread_title($value);

# スレッド名のNGの除外設定を取得
my $value = $ngthread->get_ng_thread_title_exclude();

# スレッド名のNGの除外設定をセット
$ngthread->set_ng_thread_title_exclude($value);

# スレッド作成者のNG設定に一致するかどうか
if ($ngthread->is_ng_thread_creator($thread_creator)) {
    # 一致する場合の処理
}

# スレッド名のNG設定に一致するかどうか
if ($ngthread->is_ng_thread_title($thread_title)) {
    # 一致する場合の処理
}

# 設定済みのNGスレッド設定を書込IDログ/Cookieに保存
$ngthread->save();

=head1 INTERFACE

=head2 Package Constants

=over

=item DisplayMode_Hide NGスレッド表示設定 スレッド非表示

=item DisplayMode_Replace NGスレッド表示設定 スレッド名置換

=back

1;
