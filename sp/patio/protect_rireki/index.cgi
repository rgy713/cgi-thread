#!/usr/local/bin/perl

#������������������������������������������������������������
#�� Web Protect : enter.cgi (Original) - 2011/10/02
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#������������������������������������������������������������

use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use Encode qw();
use HistoryCookie;

# �O���t�@�C����荞��
require './init.cgi';
my %cf = &init;

# �f�[�^��
my %in = &parse_form;

# ����ID Cookie
my $cookie = HistoryCookie->new();

# ���O�C���F�؎��{
if ($in{login}) {
	login();
}

# ���O�C���F�؂��s��Ȃ����̕\��
if (!defined($cookie->('HISTORY_ID'))) {
	# �����O�C�����ɁA����ID���s/����ID�F�؃t�H�[���\��
	issue_or_login_form();
} else {
	# ���Ƀ��O�C�����Ă��鎞�ɁA�A�J�E���g���/�p�X���[�h�ύX�t�H�[���\��
	account_info();
}

#-----------------------------------------------------------
#  ���O�C���F��
#-----------------------------------------------------------
sub login {
	# ID3�����ڂ̕����t�H���_�i���o�[�ƃ��[�U�[�l�[���̃Z�p���[�^�[��_�ɕϊ�����ID���擾
	my $login_id = do {
		# �}���`�o�C�g���������邱�Ƃ��l�����A�����G���R�[�h�ɕϊ�
		my $enc_cp932 = Encode::find_encoding('cp932');
		my $orig_id = $enc_cp932->decode($in{id});

		# ����ID�擪�E�����̃z���C�g�X�y�[�X������
		$orig_id =~ s/^\W+|\W+$//g;

		# ID�擪�̕����t�H���_�i���o�[�����擾���A���`
		my $folder_number = sprintf('%02d', int(substr($orig_id, 0, 2)));

		# ID�㔼�̃��[�U�[�l�[�������擾���A���`
		my $username = substr($orig_id, 3);
		$username =~ s/[^0-9a-zA-Z]//g;

		# �����t�H���_�i���o�[�ƃ��[�U�[�l�[����_������ID���č\��
		"${folder_number}_${username}";
	};

	$in{pw} =~ s/\W//g;

	# �����͂̏ꍇ
	if ($login_id eq "" || $in{pw} eq "") { &error("����ID�Ɨ����p�X���[�h����v���܂���B"); }

	# �F�؎��s
	if (!$cookie->login($login_id, $in{pw})) {
		&error("����ID�Ɨ����p�X���[�h����v���܂���B")
	}

	# ���O�L�^
	&save_log($login_id);

	# �F�؊������b�Z�[�W�\��
	message('����ID�F�؊���', '�F�؂ɐ������܂����B');
}

#-----------------------------------------------------------
#  ����ID���s/���O�C�����
#-----------------------------------------------------------
sub issue_or_login_form {
	open(IN,"$cf{tmpldir}/issue_or_login.html") or &error("open err: issue_or_login.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �u������
	$tmpl =~ s/!manager_cgi!/$cf{manager_cgi}/g;
	$tmpl =~ s/!enter_cgi!/$cf{enter_cgi}/g;

	# �\��
	print "Content-type: text/html\n\n";
	&footer($tmpl);
}

#-----------------------------------------------------------
#  ���O�C���ς݃A�J�E���g�����
#-----------------------------------------------------------
sub account_info {
	open(IN,"$cf{tmpldir}/account_info.html") or &error("open err: account_info.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# ����ID/�p�X���[�h�擾
	my $history_id = $cookie->('HISTORY_ID');
	my $history_password = $cookie->('HISTORY_PASSWORD');

	# �u������
	$tmpl =~ s/!manager_cgi!/$cf{manager_cgi}/g;
	$tmpl =~ s/!user_id!/$history_id/g;
	$tmpl =~ s/!user_password!/$history_password/g;

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
