#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� WEB PROTECT : check.cgi - 2011/10/02
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);
use File::Spec;

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
	pwdfile    => '�p�X���[�h�t�@�C��',
	logfile    => '�A�N�Z�X�����t�@�C��',
	memfile    => '����t�@�C��',
	regist_log => '����ID���O�t�@�C��',
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
	);
foreach ( keys(%dir) ) {
	if (-d $cf{$_}) {
		print "$dir{$_}�ʒu : OK<br>\n";
	} else {
		print "$dir{$_}�ʒu : NG<br>\n";
	}
}

# �e���v���[�g�t�@�C���`�F�b�N
my %tmpl = (
	issue_or_login => '����ID���s/����ID�F�؃t�H�[�� �y�[�W�e���v���[�g',
	account_info   => '�A�J�E���g���/�p�X���[�h�ύX�t�H�[�� �y�[�W�e���v���[�g',
	message        => '������� �y�[�W�e���v���[�g',
	error          => '�G���[��� �y�[�W�e���v���[�g',
	);
foreach ( keys(%tmpl) ) {
	if (-r File::Spec->catfile($cf{tmpldir}, "$_.html")) {
		print "$tmpl{$_}�ǂݍ��� : OK<br>\n";
	} else {
		print "$tmpl{$_}�ǂݍ��� : NG<br>\n";
	}
}

print "</body></html>\n";
exit;

