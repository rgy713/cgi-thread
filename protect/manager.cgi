#!/usr/local/bin/perl

#������������������������������������������������������������
#�� WEB PROTECT : manager.cgi - 2011/10/02
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#������������������������������������������������������������

use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use Jcode;
use WebProtectAuth;

# �ݒ�t�@�C����荞��
require './init.cgi';
my %cf = &init;

# �f�[�^��
my %in = &parse_form;

# ��������
if ($in{mode} eq "new_user") { &new_user; }
if ($in{mode} eq "chg_pwd") { &chg_pwd; }
if ($in{mode} eq "del_user") { &del_user; }
&error("�s���ȃA�N�Z�X�ł�");

#-----------------------------------------------------------
#  ���[�U�o�^
#-----------------------------------------------------------
sub new_user {
	# ���s����
	if ($cf{pwd_regist} > 1) { &error("�s���ȃA�N�Z�X�ł�"); }

	# �z�X�g�����擾
	my ($host,$addr) = &get_host;

	# �`�F�b�N
	my $err;
	if ($in{name} eq "") { $err .= "���O�����̓����ł�<br>"; }
	if ($in{eml1} ne $in{eml2}) { $err .= "���[���̍ē��͓��e���قȂ�܂�<br>"; }
	if ($in{eml1} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,}$/) {
		$err .= "�d�q���[���̓��͓��e���s���ł�<br>";
	}
	if (length($in{id}) < 4 || length($in{id}) > 8) {
		$err .= "���O�C��ID��4�`8�����œ��͂��Ă�������<br>";
	}
	if ($in{id} =~ /\W/) {
		$err .= "���O�C��ID�ɉp�����ȊO�̕������܂܂�Ă��܂�<br>";
	}
	if ($err) { &error($err); }

	# �V�K���[�U�[�o�^
	my @regist_result = WebProtectAuth::create($in{id}, undef, $in{name}, $in{eml1}, undef, 1);
	if($regist_result[0] != WebProtectAuth::SUCCESS) {
		if($regist_result[0] == WebProtectAuth::IS_DENY_HOST) {
			&error("���ݓo�^�x�~���ł�");
		} elsif($regist_result[0] == WebProtectAuth::REGIST_LOG_FILE_OPEN_ERROR) {
			&error("open err: $cf{regist_log}");
		} elsif($regist_result[0] == WebProtectAuth::REPEATITIVE_REGIST_LIMIT) {
			&error("�A���o�^�͂������΂炭���Ԃ������ĉ�����");
		} elsif($regist_result[0] == WebProtectAuth::IS_DENY_EMAIL_ADDRESS) {
			&error("�o�^���郁�[���A�h���X�Ƃ��Ďg�p�ł��Ȃ������񂪊܂܂�Ă��܂�");
		} elsif($regist_result[0] == WebProtectAuth::ID_FILE_OPEN_ERROR) {
			&error("open err: $cf{pwdfile}");
		} elsif($regist_result[0] == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("write err: $cf{memfile}");
		} else {
			my @err_msg;
			if($regist_result[0] & WebProtectAuth::ID_EXISTS) {
				push(@err_msg, "$in{id}�͊��ɔ��s�ςł��B����ID�����w�肭������");
			}
			if($regist_result[0] & WebProtectAuth::DUPLICATE_EMAIL_ADDRESS) {
				push(@err_msg, "$in{eml1}�͕ʂ�ID�œo�^����Ă��܂��B<br>���̃��[���A�h���X�����w�肭������");
			}
			&error(join("<br><br>", @err_msg));
		}
	}

	# ���[���{���e���v���p
	my %m;
	$m{date}  = $regist_result[2];
	$m{name}  = $in{name};
	$m{email} = $in{eml1};
	$m{host}  = $host;
	$m{id} = $in{id};
	$m{pw} = $regist_result[1];
	$m{master} = $cf{master};

	# ���[���{���e���v��
	my $mbody;
	open(IN,"$cf{tmpldir}/mail.txt") or &error("open err: mail.txt");
	while(<IN>) {
		s/!(\w+)!/$m{$1}/;

		$mbody .= $_;
	}
	close(IN);

	# �{�����R�[�h�ϊ�
	Jcode::convert(\$mbody, 'jis', 'sjis');

	# ������MIME�G���R�[�h
	my $msub = Jcode->new("�o�^�̂��ē�")->mime_encode;

	# sendmail�R�}���h
	my $scmd = "$cf{sendmail} -t -i";
	if ($cf{sendm_f} == 1) {
		$scmd .= " -f $cf{master}";
	}

	# sendmail���M
	open(MAIL,"| $scmd") or &error("���[�����M���s");
	print MAIL "To: $in{eml1}\n";
	print MAIL "From: $cf{master}\n";
	print MAIL "Cc: $cf{master}\n";
	print MAIL "Subject: $msub\n";
	print MAIL "MIME-Version: 1.0\n";
	print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
	print MAIL "Content-Transfer-Encoding: 7bit\n";
	print MAIL "X-Mailer: $cf{version}\n\n";
	print MAIL "$mbody\n";
	close(MAIL);

	# �������
	my $msg = qq|���O�C��ID�ƃp�X���[�h����<br><b>$in{eml1}</b><br>�֑��M���܂����B|;
	&message("�V�K�o�^����", $msg);
}

#-----------------------------------------------------------
#  ���[�UPW�ύX
#-----------------------------------------------------------
sub chg_pwd {
	# ���s����
	if ($cf{pwd_regist} > 2) { &error("�s���ȃA�N�Z�X�ł�"); }

	# �`�F�b�N
	my $err;
	if ($in{id} eq "") { $err .= "���O�C��ID�����̓����ł�<br>"; }
	if ($in{pw} eq "") { $err .= "���p�X���[�h�����̓����ł�<br>"; }
	if ($in{pw1} eq "") { $err .= "�V�p�X���[�h�����̓����ł�<br>"; }
	if ($in{pw1} ne $in{pw2}) { $err .= "�V�p�X���[�h�ōēx���͕����قȂ�܂�<br>";	}
	if (length($in{pw1}) > 8) { $err .= "�V�p�X���[�h�͉p����8�����ȓ��ł�<br>"; }
	if ($in{pw1} =~ /\W/) { $err .= "�p�X���[�h�͉p�����݂̂ł�<br>"; }
	if ($err) { &error($err); }

	# �p�X���[�h�ύX
	my @update_result = WebProtectAuth::update_password($in{id}, $in{pw}, $in{pw1}, 0);
	if($update_result[0] == WebProtectAuth::IS_DENY_HOST) {
		&error("���ݓo�^�x�~���ł�");
	} elsif($update_result[0] == WebProtectAuth::ID_FILE_OPEN_ERROR) {
		&error("open err: $cf{pwdfile}");
	} elsif($update_result[0] == WebProtectAuth::ID_NOTFOUND) {
		&error("�F�؂ł��܂���");
	} elsif($update_result[0] == WebProtectAuth::PASS_MISMATCH) {
		&error("�F�؂ł��܂���$in{pw}, $update_result[1]"); 
	}

	# �������
	&message("�p�X���[�h�ύX����", "�����p�����肪�Ƃ��������܂����B");
}

#-----------------------------------------------------------
#  ���[�U�폜
#-----------------------------------------------------------
sub del_user {
	# ���s����
	if ($cf{pwd_regist} > 2) { &error("�s���ȃA�N�Z�X�ł�"); }

	# �`�F�b�N
	if ($in{id} eq "" || $in{pw} eq "") {
		&error("ID�܂��̓p�X���[�h�����̓����ł�");
	}

	# �m�F���
	if ($in{job} eq "") { &del_form; }

	# ���[�U�[�폜
	my $delete_result = WebProtectAuth::delete($in{id}, $in{pw}, 0);
	if($delete_result == WebProtectAuth::ID_FILE_OPEN_ERROR) {
		&error("open err: $cf{pwdfile}");
	} elsif($delete_result == WebProtectAuth::ID_NOTFOUND) {
		&error("�F�؂ł��܂���");
	} elsif($delete_result == WebProtectAuth::PASS_MISMATCH) {
		&error("�F�؂ł��܂���");
	} elsif($delete_result == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
		&error("open errr: $cf{memfile}");
	}

	# �������
	&message("�o�^ID�폜����", "����܂ł̂����p�����肪�Ƃ��������܂����B");
}

#-----------------------------------------------------------
#  �폜�m�F���
#-----------------------------------------------------------
sub del_form {

	open(IN,"$cf{tmpldir}/conf.html") or &error("open err: conf.html");
	print "Content-type: text/html\n\n";
	while(<IN>) {
		s/!id!/$in{id}/g;
		s/!pw!/$in{pw}/g;
		s/!manager_cgi!/$cf{manager_cgi}/g;

		print;
	}
	close(IN);

	exit;
}

#-----------------------------------------------------------
#  �������
#-----------------------------------------------------------
sub message {
	my ($ttl,$msg) = @_;

	# �e���v���[�g�ǂݍ���
	open(IN,"$cf{tmpldir}/message.html") or &error("open err: message.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �u������
	$tmpl =~ s/!page_ttl!/$ttl/g;
	$tmpl =~ s/!message!/$msg/g;
	$tmpl =~ s/!back_url!/$cf{back_url}/g;

	# �\��
	print "Content-type: text/html\n\n";
	&footer($tmpl);
}

