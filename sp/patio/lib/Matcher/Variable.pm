package Matcher::Variable;
use strict;
use warnings;

use encoding 'cp932';
use open IO => ':encoding(cp932)';

use Carp qw(croak);

use Matcher;

use Exporter 'import';
our @EXPORT    = qw();
our @EXPORT_OK = qw();

sub new {
    my $class = shift;
    my ($settings_filepath) = @_;

    # �O���t�@�C���I�[�v��
    open( my $setting_fh, '<', $settings_filepath ) || croak("Open Error: $settings_filepath");
    flock( $setting_fh, 1 ) || croak("Lock Error: $settings_filepath");

    # �w�b�_�s�ǂݔ�΂�
    <$setting_fh>;

    # �p�[�X
    my @dia;
    my @dollar_0;
    my @dollar_1;
    while ( my $line = <$setting_fh> ) {
        $line =~ s/(?:\r\n|\r|\n)$//;

        my @settings = split( /\^/, $line, -1 );
        if ( scalar(@settings) != 2 ) {
            next; # 2��ł͂Ȃ����O�s�̓X�L�b�v
        }

        local ($1);
        if ( $settings[0] =~ /^([��\$])\{.*\}$/ ) {
            my $quoted_key = quotemeta( $settings[0] );
            if ( $1 eq '��' ) {
                push( @dia, [ $quoted_key, $settings[1] ] );
            } else {
                push( @dollar_0, [ $quoted_key, $settings[1] ] );
                push( @dollar_1, [ $quoted_key, $settings[1] ] );
            }
        }
    }

    # �O���t�@�C���N���[�Y
    close($setting_fh);

    # Depth 1�̂��߁A[]��()�ɒu���������n�b�V�����쐬
    foreach my $dollar_1_k_v (@dollar_1) {
        my @dollar_1_brackets = @{ Matcher::_expect_split( ${$dollar_1_k_v}[1], 0, undef() ) };
        foreach my $dollar_1_bracket (@dollar_1_brackets) {
            local $1;
            if ( $dollar_1_bracket =~ /^\[(.*)\]$/ ) {
                $dollar_1_bracket = "($1)";
            }
        }
        ${$dollar_1_k_v}[1] = join( '', @dollar_1_brackets );
    }

    my $self = {
        DIA      => \@dia,
        DOLLAR_0 => \@dollar_0,
        DOLLAR_1 => \@dollar_1
    };
    return bless $self, $class;
}

sub extract_variable {
    my ( $self, $str ) = @_;

    return $self->_extract( $str, 0 );
}

sub _extract {
    my ( $self, $str, $depth ) = @_;

    if ( $depth == 0 ) {
        my @dia      = @{ $self->{DIA} };
        my @dollar_0 = @{ $self->{DOLLAR_0} };

        my @brackets = @{ Matcher::_expect_split( $str, 0, undef() ) };
        foreach my $bracket (@brackets) {
            if ( $bracket =~ /^(?:\[.*\]|\{.*\})$/ ) {
                next;
            }
            foreach my $dia_k_v (@dia) {
                my ( $dia_key, $dia_value ) = @{$dia_k_v};
                $bracket =~ s/$dia_key/$dia_value/g;
            }
        }
        $str = join( '', @brackets );

        @brackets = @{ Matcher::_expect_split( $str, 0, undef() ) };
        foreach my $bracket (@brackets) {
            local $1;
            if ( $bracket =~ /^\{.*\}$/ ) {
                next;
            } elsif ( $bracket =~ /^\[(.*)\]$/ ) {
                $bracket = '[' . $self->_extract( $1, 1 ) . ']';
            }
            foreach my $dollar_0_k_v (@dollar_0) {
                my ( $dollar_0_key, $dollar_0_value ) = @{$dollar_0_k_v};
                $bracket =~ s/$dollar_0_key/$dollar_0_value/g;
            }
        }
        $str = join( '', @brackets );
    } else {
        my @dollar_1 = @{ $self->{DOLLAR_1} };

        my @brackets = @{ Matcher::_expect_split( $str, 1, undef() ) };
        foreach my $bracket (@brackets) {
            if ( $bracket =~ /^\{.*\}$/ ) {
                next;
            }
            foreach my $dollar_1_k_v (@dollar_1) {
                my ( $dollar_1_key, $dollar_1_value ) = @{$dollar_1_k_v};
                $bracket =~ s/$dollar_1_key/$dollar_1_value/g;
            }
        }
        $str = join( '', @brackets );
    }

    return $str;
}

1;
