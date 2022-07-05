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

# ������̈�v������s���T�u���[�`��
#
# ��1���� : ����Ώە�����̔z�񃊃t�@�����X
# ��2���� : ��v���ҕ�����̔z�񃊃t�@�����X
# ��3���� : �Ђ炪�ȁE�J�^�J�i�̑S/���p�ȊO�ɁA��/�������̋�ʂ��s�����ǂ��� (0: ��ʂ��� 1: ��ʂ��Ȃ� �萔��`)
# ��4���� : ��v�ݒ蕶����̐ړ���������̔z�񃊃t�@�����X (undef�͉����t�����Ȃ�) (['@ ', undef, undef, undef]�Ȃ�)
# ��5���� : �S��v���̐ݒ蕶����u��������̔z�񃊃t�@�����X (undef�͔���Ώۂ̕����񂻂̂܂܂Ƃ���) (['**', undef, undef, undef]�Ȃ�)
# ��6���� : �O���t�@�C���ɂ��L�[���[�h��v����ϐ��̓W�J���s���ꍇ�́AMatcher::Variable�̃C���X�^���X (����ȊO��undef)
sub match {

    # �����̎Q�ƌ^�ƁA�v�f�����S�ē����ł��邩�ǂ����m�F
    # ($match_prefixes��$all_matches�̂݁A�S�̂������͗v�f�Ƃ���undef���n���Ă����ꍇ�ɁA�������󕶎��v�f�ƂȂ�z����쐬or���삷��)
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

# 1�̔���ΏہE���ҕ�����̈�v������s��
sub _single_target_match {
    my ( $target, $expect, $match_prefix, $all_match, $hiragana_katakana_normalize_mode ) = @_;

    # �u*�v�ɂ��S�}�b�`
    if ( $expect eq '*' ) {
        if ( $all_match ne '' ) {
            return [ [ "$match_prefix$all_match", '' ] ];
        } else {
            return [ [ "$match_prefix$target", '' ] ];
        }
    }

    # ��v����ƈ�v������擾�̂��߁A
    # ���K����������Ώ�/���ҕ�����ƁA���K��������̊e1�����ɑΉ����錳������̔z�񃊃t�@�����X���擾
    my ( $normalized_target, $orig_target_chars ) = @{ _normalize_string_for_match( $target, $hiragana_katakana_normalize_mode ) };
    my ( $normalized_expect, $orig_expect_chars ) = @{ _normalize_string_for_match( $expect, $hiragana_katakana_normalize_mode ) };

    # OR�������Ƃɕ��������p�^�[�����쐬
    my @or_expect = @{ _or_split( $normalized_expect, 0 ) };

    # {}�݂̂̊��S��v����
    my $perfect_match_flag = '';
    if ( scalar(@or_expect) == 1 ) {
        my $tmp_orig_expect = ${ $or_expect[0] }[0];
        my @tmp_and = @{ _and_split( $tmp_orig_expect, 0 ) };
        if ( scalar(@tmp_and) == 1 && $tmp_and[0] =~ /^\{.[^}]*\}$/ ) {
            $or_expect[0] = [ $tmp_orig_expect, 1, 1 ];
            $perfect_match_flag = 1;
        }
    }

    # OR�������Ƃɕ����������K�\�����쐬
    my @or_regexp = @{ _create_regexp( \@or_expect, 0 ) };

    # OR�������Ƃ́A���ʌ����p�p�^�[����������쐬
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

    # OR�������ƂɃ}�b�`�E�L���v�`�����s
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

            # AND�����ʂɂȂ��Ă���אڂ����v���ʂ��A����Ώە��������ɂł��邾������
            @match_capture = @{ _concat_match_result( $target, \@match_capture ) };

            # ��vAND�����𕶎����
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

# ����($separator���w�莞) �������� $separator�ŕ�������T�u���[�`��
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
                && ( $queue eq '' || ( substr( $queue, length($queue) - 1, 1 ) ne '��' && substr( $queue, length($queue) - 1, 1 ) ne '$' ) )
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

# OR��������
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

# AND��������
sub _and_split {
    my ( $expect, $depth ) = @_;

    return _expect_split( $expect, $depth, '_' );
}

# 1��AND���������K�\���쐬
# (���ʃO���[�v�����o�����͂��̉ӏ��ɂ��čċA�I�ɍ쐬)
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

# 1��OR�������K�\���쐬
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

# �S�̂̐��K�\���쐬
sub _create_regexp {
    my ( $or_expects, $depth ) = @_;

    my @regexps = map { _in_or_regexp( $_, $depth ) } @{$or_expects};
    return \@regexps;
}

# �}�b�`�̂��߂̕����񐳋K�����s���A
# [���K���㕶����, ���K���㕶�����1�����ɑ�������I���W�i��������z��v�f�̃��t�@�����X] ��Ԃ�
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

        # ���p�J�^�J�i��S�p�J�^�J�i�ɕϊ�
        my $conv_char = katakana_h2z($orig_char);
        if ( length($conv_char) == 2 ) {
            $orig_char = substr( $orig_char, 0, 1 );
            $conv_char = substr( $conv_char, 0, 1 );
            $i++;
        } else {
            $i += 2;
        }

        # �����ɂ���āA�Ђ炪�ȁE�J�^�J�i�����ׂđS�p�啶���ɕϊ�
        if ( $hiragana_katakana_normalize_mode == STRING_NORMALIZE_HIRAGANA_KATAKANA_NOT_CASE_SENSITIVE ) {
            $conv_char =~ tr/�����������������@�B�D�F�H�����b��������/���������������A�C�E�G�I�J�P�c��������/;
        }

        # �p������S�Ĕ��p�������ɕϊ�
        $conv_char =~ tr/A-Z��-���`-�y�O-�X/a-za-za-z0-9/;

        # 1����(�ϊ���)�ɑ�������I���W�i��������̔z����쐬
        push( @orig_chars, $orig_char );

        $ret_string .= $conv_char;
    }

    return [ $ret_string, \@orig_chars ];
}

# ���莞OR���[�v���}�b�`�אڐݒ�l�A�����s�T�u���[�`��
# ��1����: ����Ώە�����
# ��2����: AND�������ƈ�v������z�񃊃t�@�����X
# �Ԃ�l: �אڐݒ�l�A����̈�v������z�񃊃t�@�����X(�z��\���͑�2�����Ɠ��������A�A�����ꂽ�v�f�͍폜���ꂽ�`)
sub _concat_match_result {
    my ( $check_str, $match_str_array_ref ) = @_;
    my @match_str_array = @{$match_str_array_ref};

    # �ݒ�l�̗אڊ֌W�Ɠ�����v��������������čŌ��index�ƂƂ��ɕԂ��܂�
    # �Œ���v�A���A��Ɉ�v�����������D�悵�Č������܂�
    #
    # $self: �������g�̕ϐ�(�����֐��ϐ��E�ċA�ďo�ɕK�v)
    # $current_index: ���݂�index (�ŏ��ɌĂԍۂ́A�������n�߂�index��^���ĉ�����)
    # $concat_test_str_array: �Oindex�̈�v������z��
    # �Ԃ�l: ����������v������ƌ��������Ō��index (�����ł��Ȃ������ꍇ��undef)
    my $try_neighbor_concat = sub {
        my ( $self, $current_index, $concat_test_str_array_ref ) = @_;

        # �Oindex������ꍇ�́A����index�̈�v�����������������v����������z����쐬
        # (�Oindex���Ȃ��ꍇ�͌���index�̈�v������z������̂܂܎g�p����)
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

        # ��index������ꍇ�́A�ċA�I�ɌĂяo���Č��������A��v�����ꍇ�͂��̕Ԃ�l�����̂܂ܕԂ�
        my $next_index = $current_index + 1;
        if ( $next_index < scalar(@match_str_array) ) {
            my $next_index_concat_str_index_array_ref = $self->( $self, $next_index, \@joined_test_str_array );
            if ( defined($next_index_concat_str_index_array_ref) ) {
                return $next_index_concat_str_index_array_ref;
            }
        }

        # ���݂̈�v����������ƈ�v���邩���肵�āA
        # ��v�����炻�̕������index�̔z�񃊃t�@�����X���A
        # �����łȂ����undef��Ԃ�
        if ( defined($concat_test_str_array_ref) ) {
            foreach my $joined_test_str (@joined_test_str_array) {
                if ( index( $check_str, $joined_test_str ) != -1 ) {
                    return [ $joined_test_str, $current_index ];
                }
            }
        }
        return;
    };

    my $concat_try_index = 0; # �������sindex
    my @joined_match_str;
    for ( ; $concat_try_index < scalar(@match_str_array); ) {

        # ���������݂�
        my $matched_concat_str_index_array_ref = $try_neighbor_concat->( $try_neighbor_concat, $concat_try_index );
        if ( defined($matched_concat_str_index_array_ref) ) {
            push( @joined_match_str, ${$matched_concat_str_index_array_ref}[0] );
            $concat_try_index = ${$matched_concat_str_index_array_ref}[1] + 1;
        } else {

            # �����ł��Ȃ�����������͂��̂܂܂ɂ���
            push( @joined_match_str, $match_str_array[$concat_try_index] );
            $concat_try_index++;
        }
    }

    # ������̔z����쐬
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
