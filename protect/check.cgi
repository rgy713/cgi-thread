#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� WEB PROTECT : check.cgi - 2011/10/02
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �ݒ�f�[�^�F��
require "./init.cgi";
my %cf = &init;

print <<EOM;
Content-type: text/html

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
EOM


# �t�@�C���`�F�b�N
my %name = (
	pwdfile => '�p�X���[�h�t�@�C��',
	logfile => '�A�N�Z�X�����t�@�C��',
	memfile => '����t�@�C��',
	regist_log => '�A�����[�U�[�o�^�����`�F�b�N���O�t�@�C��'
	);
foreach ( keys(%name) ) {
	if (-f $cf{$_}) {
		print "$name{$_}�ʒu: OK<br>\n";

		if (-r $cf{$_} && -w $cf{$_}) {
			print "$name{$_}�p�[�~�b�V����: OK<br>\n";
		} else {
			print "$name{$_}�p�[�~�b�V����: NG<br>\n";
		}
	} else {
		print "$name{$_}�ʒu: NG<br>\n";
	}
}

# �t�H���_�ʒu
my %dir = (
	tmpldir => '�e���v���[�g�f�B���N�g��',
	prvdir  => '�B���f�B���N�g��',
	sesdir  => '�Z�b�V�����f�B���N�g��',
	);
foreach ( keys(%dir) ) {
	if (-d $cf{$_}) {
		print "$dir{$_}�ʒu : OK<br>\n";

		# �Z�b�V�����f�B���N�g���̓p�[�~�b�V�����m�F
		if ($_ eq 'sesdir') {
			if (-r "$cf{$_}" && -r "$cf{$_}" && -r "$cf{$_}") {
				print "$dir{$_}�p�[�~�b�V���� : OK<br>\n";
			} else {
				print "$dir{$_}�p�[�~�b�V���� : NG<br>\n";
			}
		}

	} else {
		print "$dir{$_}�ʒu : NG<br>\n";
	}
}

# sendmail
if (-e $cf{sendmail}) {
	print "sendmail�ʒu : OK<br>\n";
} else {
	print "sendmail�ʒu : NG<br>\n";
}

print "</body></html>\n";
exit;

