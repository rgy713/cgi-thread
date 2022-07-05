package Matcher;
use strict;
use warnings;

use encoding 'cp932';

use Carp qw(confess);
use List::MoreUtils qw(any each_array pairwise uniq);
use Scalar::Util qw(blessed);

use Lingua::JA::Regular::Unicode qw(katakana_h2z);
use Math::Combinatorics qw(permute);

use Exporter 'import';
our @EXPORT    = qw();
our @EXPORT_OK = qw(match);

use constant {
    STRING_NORMALIZE_HIRAGANA_KATAKANA_CASE_SENSITIVE     => 0,
    STRING_NORMALIZE_HIRAGANA_KATAKANA_NOT_CASE_SENSITIVE => 1
};

# 文字列の一致判定を行うサブルーチン
#
# 第1引数 : 判定対象文字列の配列リファレンス
# 第2引数 : 一致期待文字列の配列リファレンス
# 第3引数 : ひらがな・カタカナの全/半角以外に、大/小文字の区別を行うかどうか (0: 区別する 1: 区別しない 定数定義)
# 第4引数 : 一致設定文字列の接頭詞文字列の配列リファレンス (undefは何も付加しない) (['@ ', undef, undef, undef]など)
# 第5引数 : 全一致時の設定文字列置換文字列の配列リファレンス (undefは判定対象の文字列そのままとする) (['**', undef, undef, undef]など)
# 第6引数 : 外部ファイルによるキーワード一致判定変数の展開を行う場合は、Matcher::Variableのインスタンス (それ以外はundef)
sub match {

    # 引数の参照型と、要素数が全て同じであるかどうか確認
    # ($match_prefixesと$all_matchesのみ、全体もしくは要素としてundefが渡ってきた場合に、そこが空文字要素となる配列を作成or操作する)
    my ( $targets, $expects, $hiragana_katakana_normalize_mode, $match_prefixes, $all_matches, $variable ) = @_;
    if ( ref($targets) ne 'ARRAY' ) {
        confess('$targets is not ARRAY.');
    }
    if ( ref($expects) ne 'ARRAY' ) {
        confess('$expects is not ARRAY.');
    }
    if (!defined($hiragana_katakana_normalize_mode)
        || (   $hiragana_katakana_normalize_mode != STRING_NORMALIZE_HIRAGANA_KATAKANA_CASE_SENSITIVE
            && $hiragana_katakana_normalize_mode != STRING_NORMALIZE_HIRAGANA_KATAKANA_NOT_CASE_SENSITIVE )
        )
    {
        confess('$hiragana_katakana_normalize_mode must be set 0 or 1.');
    }
    my $targets_len = scalar( @{$targets} );
    if ( ( my $expects_len = scalar( @{$expects} ) ) != $targets_len ) {
        confess( sprintf( '$expects(len: %d) != $targets(len: %d)', $expects_len, $targets_len ) );
    }
    if ( defined($match_prefixes) ) {
        if ( ref($match_prefixes) ne 'ARRAY' ) {
            confess('$match_prefixes is not ARRAY.');
        }
        if ( ( my $match_prefixes_len = scalar( @{$match_prefixes} ) ) != $targets_len ) {
            confess( sprintf( '$match_prefixes(len: %d) != $targets(len: %d)', $match_prefixes_len, $targets_len ) );
        }
        $match_prefixes = [ map { defined($_) ? $_ : '' } @{$match_prefixes} ];
    } else {
        $match_prefixes = [ ('') x $targets_len ];
    }
    if ( defined($all_matches) ) {
        if ( ref($all_matches) ne 'ARRAY' ) {
            confess('$all_matches is not ARRAY.');
        }
        if ( ( my $all_matches_len = scalar( @{$all_matches} ) ) != $targets_len ) {
            confess( sprintf( '$all_matches(len: %d) != $targets(len: %d)', $all_matches_len, $targets_len ) );
        }
        $all_matches = [ map { defined($_) ? $_ : '' } @{$all_matches} ];
    } else {
        $all_matches = [ ('') x $targets_len ];
    }
    if ( defined($variable) && ( !blessed($variable) || !$variable->isa('Matcher::Variable') ) ) {
        confess('$variable is not Matcher::Variable instance.');
    }

    my $match_set_iterator = each_array( @{$targets}, @{$expects}, @{$match_prefixes}, @{$all_matches} );
    my @result;
    while ( my @match_args = $match_set_iterator->() ) {
        if ( defined($variable) ) {
            $match_args[1] = $variable->extract_variable( $match_args[1] );
        }
        my $single_match_result = _single_target_match( @match_args, $hiragana_katakana_normalize_mode );
        push( @result, $single_match_result );
    }

    if ( any { defined($_) } @result ) {
        return \@result;
    } else {
        return;
    }
}

# 1つの判定対象・期待文字列の一致判定を行う
sub _single_target_match {
    my ( $target, $expect, $match_prefix, $all_match, $hiragana_katakana_normalize_mode ) = @_;

    # 「*」による全マッチ
    if ( $expect eq '*' ) {
        if ( $all_match ne '' ) {
            return [ [ "$match_prefix$all_match", '' ] ];
        } else {
            return [ [ "$match_prefix$target", '' ] ];
        }
    }

    # 一致判定と一致文字列取得のため、
    # 正規化した判定対象/期待文字列と、正規化文字列の各1文字に対応する元文字列の配列リファレンスを取得
    my ( $normalized_target, $orig_target_chars ) = @{ _normalize_string_for_match( $target, $hiragana_katakana_normalize_mode ) };
    my ( $normalized_expect, $orig_expect_chars ) = @{ _normalize_string_for_match( $expect, $hiragana_katakana_normalize_mode ) };

    # OR条件ごとに分割したパターンを作成
    my @or_expect = @{ _or_split( $normalized_expect, 0 ) };

    # {}のみの完全一致判定
    my $perfect_match_flag = '';
    if ( scalar(@or_expect) == 1 ) {
        my $tmp_orig_expect = ${ $or_expect[0] }[0];
        my @tmp_and = @{ _and_split( $tmp_orig_expect, 0 ) };
        if ( scalar(@tmp_and) == 1 && $tmp_and[0] =~ /^\{.[^}]*\}$/ ) {
            $or_expect[0] = [ $tmp_orig_expect, 1, 1 ];
            $perfect_match_flag = 1;
        }
    }

    # OR条件ごとに分割した正規表現を作成
    my @or_regexp = @{ _create_regexp( \@or_expect, 0 ) };

    # OR条件ごとの、結果結合用パターン文字列を作成
    my @or_expect_for_return;
    for ( my ( $i, $k ) = ( 0, 0 ); $i < scalar(@or_expect); $i++ ) {
        my ( $pattern, $head_match_flag, $tail_match_flag ) = @{ $or_expect[$i] };
        my $ptn_len = length($pattern);
        if ( $i == 0 && $head_match_flag && !$perfect_match_flag ) {
            $ptn_len++;
        }
        if ( $i == $#or_expect && $tail_match_flag && !$perfect_match_flag ) {
            $ptn_len++;
        }
        my $orig_pattern = join( '', @{$orig_expect_chars}[ $k .. $k + $ptn_len - 1 ] );
        push( @or_expect_for_return, $orig_pattern );
        $k += $ptn_len + 1;
    }

    # OR条件ごとにマッチ・キャプチャ実行
    my @or_match;
    foreach my $pair ( pairwise { [ $a, $b ] } @or_regexp, @or_expect_for_return ) {
        my ( $single_or_regexp, $single_or_expect ) = @{$pair};

        if ( $normalized_target =~ /$single_or_regexp/ ) {
            my @match_capture;
            foreach my $i ( 1 .. $#+ ) {
                if ( !defined( $-[$i] ) ) {
                    next;
                }
                push( @match_capture, join( '', @{$orig_target_chars}[ $-[$i] .. $+[$i] - 1 ] ) );
            }

            # AND条件別になっている隣接する一致結果を、判定対象文字列を基にできるだけ結合
            @match_capture = @{ _concat_match_result( $target, \@match_capture ) };

            # 一致AND条件を文字列に
            my $and_joined_match_orig_target = join( '_', @match_capture );

            push( @or_match, [ "$match_prefix$single_or_expect", $and_joined_match_orig_target ] );
        }
    }

    if ( scalar(@or_match) >= 1 ) {
        return \@or_match;
    } else {
        return;
    }
}

# 括弧($separator未指定時) もしくは $separatorで分割するサブルーチン
sub _expect_split {
    my ( $expect, $depth, $separator ) = @_;

    my @sentences;
    my $end_bracket_char = '';
    my $queue            = '';
    for ( my $i = 0; $i < length($expect); ) {
        my $char = substr( $expect, $i, 1 );
        if ( $end_bracket_char eq '' ) {
            if ( $depth == 0 && $char eq '[' ) {
                $end_bracket_char = ']';
                if ( !defined($separator) && $queue ne '' ) {
                    push( @sentences, $queue );
                    $queue = '';
                }
                $queue .= $char;
            } elsif ( $depth == 1 && $char eq '(' ) {
                $end_bracket_char = ')';
                if ( !defined($separator) && $queue ne '' ) {
                    push( @sentences, $queue );
                    $queue = '';
                }
                $queue .= $char;
            } elsif ( $depth <= 2
                && $char eq '{'
                && ( $queue eq '' || ( substr( $queue, length($queue) - 1, 1 ) ne '◆' && substr( $queue, length($queue) - 1, 1 ) ne '$' ) )
                )
            {
                my $brace_str_length = index( substr( $expect, $i ), '}' ) + 1;
                if ( $brace_str_length >= 1 ) {
                    if ( !defined($separator) ) {
                        if ( $queue ne '' ) {
                            push( @sentences, $queue );
                            $queue = '';
                        }
                        push( @sentences, substr( $expect, $i, $brace_str_length ) );
                    } else {
                        $queue .= substr( $expect, $i, $brace_str_length );
                    }
                    $i += $brace_str_length;
                    next;
                }
            } elsif ( defined($separator) && $char eq $separator ) {
                if ( $queue ne '' ) {
                    push( @sentences, $queue );
                    $queue = '';
                }
            } else {
                $queue .= $char;
            }
        } else {
            if ( $char eq $end_bracket_char ) {
                $end_bracket_char = '';
                $queue .= $char;
                if ( !defined($separator) && $queue ne '' ) {
                    push( @sentences, $queue );
                    $queue = '';
                }
            } elsif ( $char eq '{' ) {
                my $brace_str_length = index( substr( $expect, $i ), '}' ) + 1;
                if ( $brace_str_length >= 1 ) {
                    $queue .= substr( $expect, $i, $brace_str_length );
                    $i += $brace_str_length;
                    next;
                } else {
                    $queue .= $char;
                }
            } else {
                $queue .= $char;
            }
        }
        $i++;
    }
    if ( $queue ne '' ) {
        push( @sentences, $queue );
    }
    return \@sentences;
}

# OR条件分割
sub _or_split {
    my ( $expect, $depth ) = @_;
    my $separator = $depth == 0 ? ',' : '|';

    my @tmp_or = @{ _expect_split( $expect, $depth, $separator ) };
    my @or;
    foreach my $or_expect (@tmp_or) {
        local ( $1, $2, $3 );
        $or_expect =~ /^(\~)?(.*?)(\$)?$/;
        my $head_match_flag = $depth == 0 && defined($1) && $1 eq '~';
        my $tail_match_flag = $depth == 0 && defined($3) && $3 eq '$';
        push( @or, [ $2, $head_match_flag, $tail_match_flag ] );
    }

    return \@or;
}

# AND条件分割
sub _and_split {
    my ( $expect, $depth ) = @_;

    return _expect_split( $expect, $depth, '_' );
}

# 1つのAND条件内正規表現作成
# (下位グループ条件出現時はその箇所について再帰的に作成)
sub _in_and_regexp {
    my ( $expect, $depth ) = @_;

    my @tmp_group = @{ _expect_split( $expect, $depth, undef() ) };
    my $regexp;
    foreach my $str (@tmp_group) {
        local ( $1, $2 );
        if ( $depth == 0 && $str =~ /^\[(.*?)\]$/ ) {
            if ( index( $1, '|' ) == -1 ) {
                $regexp .= '[' . quotemeta($1) . ']';
            } else {
                my $or_expects = _or_split( $1, 1 );
                $regexp .= '(?:' . join( '|', @{ _create_regexp( $or_expects, 1 ) } ) . ')';
            }
        } elsif ( $depth == 1 && $str =~ /^\((.*?)\)$/ ) {
            if ( index( $1, '|' ) == -1 ) {
                $regexp .= '[' . quotemeta($1) . ']';
            } else {
                my $or_expects = _or_split( $1, 2 );
                $regexp .= '(?:' . join( '|', @{ _create_regexp( $or_expects, 2 ) } ) . ')';
            }
        } elsif ( $depth <= 2 && $str =~ /^(\{(.*?)\})$/ ) {
            $regexp .= '(?:' . quotemeta($2) . ')';
        } else {
            $str = quotemeta($str);
            $str =~ s/\\([.?])/$1/g;
            $regexp .= $str;
        }
    }

    if ( $depth == 0 ) {
        $regexp = "($regexp)";
    }

    return $regexp;
}

# 1つのOR条件正規表現作成
sub _in_or_regexp {
    my ( $or_set, $depth ) = @_;
    my ( $or, $head_match_flag, $tail_match_flag ) = @{$or_set};

    my @and_permutation = permute( @{ _and_split( $or, $depth ) } );

    my @regexp_permutation;
    foreach my $and_set (@and_permutation) {
        my @and            = @{$and_set};
        my $current_regexp = '';
        for ( my $i = 0; $i < scalar(@and); $i++ ) {
            if ( $i == 0 ) {
                if ( $depth == 0 && $head_match_flag ) {
                    $current_regexp .= '^';
                }
            } else {
                $current_regexp .= '.*?';
            }

            my $in_and_regexp = _in_and_regexp( $and[$i], $depth );
            $current_regexp .= $in_and_regexp;

            if ( $i == $#and && $depth == 0 && $tail_match_flag ) {
                $current_regexp .= '$';
            }
        }
        if ( scalar(@and) >= 2 ) {
            $current_regexp = "(?:$current_regexp)";
        }
        push( @regexp_permutation, $current_regexp );
    }
    @regexp_permutation = uniq(@regexp_permutation);

    my $regexp;
    if ( scalar(@regexp_permutation) >= 2 ) {
        $regexp = '(?:' . join( '|', @regexp_permutation ) . ')';
    } else {
        $regexp = join( '', @regexp_permutation );
    }
    return $regexp;
}

# 全体の正規表現作成
sub _create_regexp {
    my ( $or_expects, $depth ) = @_;

    my @regexps = map { _in_or_regexp( $_, $depth ) } @{$or_expects};
    return \@regexps;
}

# マッチのための文字列正規化を行い、
# [正規化後文字列, 正規化後文字列の1文字に相当するオリジナル文字列配列要素のリファレンス] を返す
sub _normalize_string_for_match {
    my ( $string, $hiragana_katakana_normalize_mode ) = @_;
    my $str_len = length($string);

    my @orig_chars;
    my $ret_string = '';
    for ( my $i = 0; $i < $str_len; ) {
        my $orig_char;
        if ( $i < $str_len - 1 ) {
            $orig_char = substr( $string, $i, 2 );
        } else {
            $orig_char .= substr( $string, $i, 1 );
        }

        # 半角カタカナを全角カタカナに変換
        my $conv_char = katakana_h2z($orig_char);
        if ( length($conv_char) == 2 ) {
            $orig_char = substr( $orig_char, 0, 1 );
            $conv_char = substr( $conv_char, 0, 1 );
            $i++;
        } else {
            $i += 2;
        }

        # 引数によって、ひらがな・カタカナをすべて全角大文字に変換
        if ( $hiragana_katakana_normalize_mode == STRING_NORMALIZE_HIRAGANA_KATAKANA_NOT_CASE_SENSITIVE ) {
            $conv_char =~ tr/ぁぃぅぇぉっゃゅょゎァィゥェォヵヶッャュョヮ/あいうえおつやゆよわアイウエオカケツヤユヨワ/;
        }

        # 英数字を全て半角小文字に変換
        $conv_char =~ tr/A-Zａ-ｚＡ-Ｚ０-９/a-za-za-z0-9/;

        # 1文字(変換後)に相当するオリジナル文字列の配列を作成
        push( @orig_chars, $orig_char );

        $ret_string .= $conv_char;
    }

    return [ $ret_string, \@orig_chars ];
}

# 判定時ORループ内マッチ隣接設定値連結試行サブルーチン
# 第1引数: 判定対象文字列
# 第2引数: AND条件ごと一致文字列配列リファレンス
# 返り値: 隣接設定値連結後の一致文字列配列リファレンス(配列構造は第2引数と同じだが、連結された要素は削除された形)
sub _concat_match_result {
    my ( $check_str, $match_str_array_ref ) = @_;
    my @match_str_array = @{$match_str_array_ref};

    # 設定値の隣接関係と同じ一致文字列を結合して最後のindexとともに返します
    # 最長一致、かつ、先に一致した文字列を優先して結合します
    #
    # $self: 自分自身の変数(無名関数変数・再帰呼出に必要)
    # $current_index: 現在のindex (最初に呼ぶ際は、検索を始めるindexを与えて下さい)
    # $concat_test_str_array: 前indexの一致文字列配列
    # 返り値: 結合した一致文字列と結合した最後のindex (結合できなかった場合はundef)
    my $try_neighbor_concat = sub {
        my ( $self, $current_index, $concat_test_str_array_ref ) = @_;

        # 前indexがある場合は、現在indexの一致文字列を結合した一致結合文字列配列を作成
        # (前indexがない場合は現在indexの一致文字列配列をそのまま使用する)
        my @joined_test_str_array;
        if ( defined($concat_test_str_array_ref) ) {
            foreach my $concat_test_str ( @{$concat_test_str_array_ref} ) {
                foreach my $test_str (@match_str_array) {
                    push( @joined_test_str_array, $concat_test_str . $test_str );
                }
            }
        } else {
            @joined_test_str_array = $match_str_array[$current_index];
        }

        # 後indexがある場合は、再帰的に呼び出して結合させ、一致した場合はその返り値をそのまま返す
        my $next_index = $current_index + 1;
        if ( $next_index < scalar(@match_str_array) ) {
            my $next_index_concat_str_index_array_ref = $self->( $self, $next_index, \@joined_test_str_array );
            if ( defined($next_index_concat_str_index_array_ref) ) {
                return $next_index_concat_str_index_array_ref;
            }
        }

        # 現在の一致結合文字列と一致するか判定して、
        # 一致したらその文字列とindexの配列リファレンスを、
        # そうでなければundefを返す
        if ( defined($concat_test_str_array_ref) ) {
            foreach my $joined_test_str (@joined_test_str_array) {
                if ( index( $check_str, $joined_test_str ) != -1 ) {
                    return [ $joined_test_str, $current_index ];
                }
            }
        }
        return;
    };

    my $concat_try_index = 0; # 結合試行index
    my @joined_match_str;
    for ( ; $concat_try_index < scalar(@match_str_array); ) {

        # 結合を試みる
        my $matched_concat_str_index_array_ref = $try_neighbor_concat->( $try_neighbor_concat, $concat_try_index );
        if ( defined($matched_concat_str_index_array_ref) ) {
            push( @joined_match_str, ${$matched_concat_str_index_array_ref}[0] );
            $concat_try_index = ${$matched_concat_str_index_array_ref}[1] + 1;
        } else {

            # 結合できなかった文字列はそのままにする
            push( @joined_match_str, $match_str_array[$concat_try_index] );
            $concat_try_index++;
        }
    }

    # 結合後の配列を作成
    if ( scalar(@joined_match_str) > 0 ) {
        if ( $concat_try_index != scalar(@match_str_array) ) {
            @match_str_array = ( @joined_match_str, @match_str_array[ $concat_try_index .. $#match_str_array ] );
        } else {
            @match_str_array = @joined_match_str;
        }
    }

    return \@match_str_array;
}

1;
