#!/usr/local/bin/perl

#������������������������������������������������������������
#�� WEB PROTECT : protect.cgi - 2011/10/02
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#������������������������������������������������������������

use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Session;

# �O���t�@�C����荞��
require './init.cgi';
my %cf = &init;

# �f�[�^��
my %in = &parse_form;

# �A�N�Z�X�F��
&cert_access;

#-----------------------------------------------------------
#  �A�N�Z�X�F��
#-----------------------------------------------------------
sub cert_access {
	# �Z�b�V�����F��
	my $ses = CGI::Session->load(undef, undef, {Directory => $cf{sesdir}});

	# ���O�A�E�g
	if ($in{mode} eq 'logout') {
		$ses->delete();

		# ������ʂɖ߂�
		&redirect($cf{enter_cgi});
	}

	# �����؂�
	if ( $ses->is_expired || $ses->is_empty ) {
		my $data = qq|<p>[<a href="$cf{enter_cgi}">���O�C������</a>]</p>|;
		&error("�^�C���A�E�g�ł��B�ēx���O�C�����Ă��������B", $data);
   	}

	# �B���t�@�C���o��
	&open_file;
}

#-----------------------------------------------------------
#  �F�؃y�[�W�\��
#-----------------------------------------------------------
sub open_file {
	# �o�C�i���t�@�C��
	my %bin = %{$cf{binary}};
	my ($flg,$key,$val);
	foreach ( keys(%in) ) {
		if (defined($bin{$_})) {
			$flg++;
			$key = $_;
			$val = $in{$_};
			last;
		}
	}
	if ($flg) { &bin_out($key,$val); }

	# �Ώۃt�@�C����`
	my $page = $in{page} || '0';
	my $target = ${$cf{secret}}[$page];

	# CGI�t�@�C���Ȃ烊�_�C���N�g
	if ($target =~ m|https?://|) {
		&redirect($target);

	# HTML�t�@�C���Ȃ�ǂݏo��
	} else {
		open(IN,"$cf{prvdir}/$target") or &error("open err: $target");
		print "Content-type: text/html\n\n";
		print <IN>;
		close(IN);

		exit;
	}
}

#-----------------------------------------------------------
#  �o�C�i���o��
#-----------------------------------------------------------
sub bin_out {
	my ($key,$val) = @_;

	# �w�b�_�[/�g���q
	my ($head,$ext) = split(/,/, ${$cf{binary}}{$key});

	# �ǂݏo��
	open(IN,"$cf{prvdir}/$val.$ext") || die;
	print "Content-type: $head\n";
	print "Content-Disposition: attachment; filename=\"$val.$ext\"\n\n";
	binmode(IN);
	binmode(STDOUT);
	print <IN>;
	close(IN);

	exit;
}

#-----------------------------------------------------------
#  ���_�C���N�g
#-----------------------------------------------------------
sub redirect {
	my $uri = shift;

	# PerlIS�Ή�
	if ($ENV{PERLXS} eq "PerlIS") {
		print "HTTP/1.0 302 Temporary Redirection\r\n";
		print "Content-type: text/html\n";
	}
	# ���_�C���N�g
	print "Location: $uri\n\n";
	exit;
}

