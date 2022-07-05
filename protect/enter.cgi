#!/usr/local/bin/perl

#������������������������������������������������������������
#�� Web Protect : enter.cgi - 2011/10/02
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#������������������������������������������������������������

use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Session;
use WebProtectAuth;

# �O���t�@�C����荞��
require './init.cgi';
my %cf = &init;

# �f�[�^��
my %in = &parse_form;

if ($in{login}) { &login; }
&enter_form;

#-----------------------------------------------------------
#  ���O�C���F��
#-----------------------------------------------------------
sub login {
	$in{id} =~ s/\W//g;
	$in{pw} =~ s/\W//g;

	# �����͂̏ꍇ
	if ($in{id} eq "" || $in{pw} eq "") { &error("�F�؂ł��܂���"); }

	# �F�؏���
	my $auth_result = WebProtectAuth::authenticate($in{id}, $in{pw});
	if($auth_result == WebProtectAuth::ID_FILE_OPEN_ERROR) {
			&error("open err: $cf{pwdfile}");
	} elsif($auth_result != WebProtectAuth::SUCCESS) {
			&error("�F�؂ł��܂���");
	}

	# �V�K�Z�b�V�������s
	my $ses = new CGI::Session(undef, undef, {Directory => $cf{sesdir}}) or die CGI::Session->errstr;

	# �L������
	my $jobtime = $cf{job_time} * 60;
	$ses->expire($jobtime);

	# �Z�b�V����ID
	my $sid = $ses->id();

	# ���O�L�^
	&save_log($in{id});

	# ���_�C���N�g
	# PerlIS�Ή�
	if ($ENV{PERLXS} eq "PerlIS") {
		print "HTTP/1.0 302 Temporary Redirection\r\n";
		print "Content-type: text/html\n";
	}
	print "Set-Cookie: CGISESSID=$sid;\n";
	print "Location: $cf{protect_cgi}\n\n";
	exit;
}

#-----------------------------------------------------------
#  �F�؉��
#-----------------------------------------------------------
sub enter_form {
	open(IN,"$cf{tmpldir}/enter.html") or &error("open err: enter.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �u������
	$tmpl =~ s/!enter_cgi!/$cf{enter_cgi}/;

	# �\��
	print "Content-type: text/html\n\n";
	&footer($tmpl);
}

#-----------------------------------------------------------
#  ���O�L�^
#-----------------------------------------------------------
sub save_log {
	my $id = shift;

	# ����/�z�X�g�擾
	my ($time,$date) = &get_time;
	my ($host,$addr) = &get_host;

	# �u���E�U���
	my $agent = $ENV{HTTP_USER_AGENT};
	$agent =~ s/[<>&"']//g;

	# ���O�t�@�C���X�V
	my $i = 0;
	my @data;
	open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";
	while(<DAT>) {
		$i++;
		push(@data,$_);

		# �ő�ۑ���
		last if ($i >= $cf{max_log} - 1);
	}
	seek(DAT, 0, 0);
	print DAT "$id<>$date<>$host<>$agent<>$time<>\n";
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);
}


