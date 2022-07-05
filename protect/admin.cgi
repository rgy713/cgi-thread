#!/usr/local/bin/perl

#������������������������������������������������������������
#�� WEB PROTECT : admin.cgi - 2013/04/06
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Session::ExpireSessions;
use Jcode;
use WebProtectAuth;

# �O���t�@�C����荞��
require './init.cgi';
my %cf = &init;

# �f�[�^��
my %in = &parse_form;

# �F��
&check_passwd;

# ��������
if ($in{data_new}) { &data_new; }
if ($in{data_mente}) { &data_mente; }
if ($in{look_log}) { &look_log; }
if ($in{exp_ses}) { &exp_ses; }

# ���j���[���
&menu_html;

#-----------------------------------------------------------
#  ���j���[���
#-----------------------------------------------------------
sub menu_html {
	&header("���j���[TOP");

	print <<EOM;
<div align="center">
<p>�I���{�^���������Ă��������B</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<table border="1" cellpadding="5" cellspacing="0">
<tr>
	<th bgcolor="#cccccc">�I��</th>
	<th bgcolor="#cccccc" width="250">�������j���[</th>
</tr><tr>
	<th><input type="submit" name="data_new" value="�I��"></th>
	<td>�V�K����o�^�쐬</td>
</tr><tr>
	<th><input type="submit" name="data_mente" value="�I��"></th>
	<td>����o�^�����e�i���X�i�C���E�폜�j</td>
</tr><tr>
	<th><input type="submit" name="look_log" value="�I��"></th>
	<td>�A�N�Z�X���O�{��</td>
</tr><tr>
	<th><input type="submit" name="exp_ses" value="�I��"></th>
	<td>�Z�b�V�����t�@�C���|��</td>
</tr><tr>
	<th><input type="button" value="�I��" onclick="javascript:window.location='$cf{admin_cgi}'"></th>
	<td>���O�A�E�g</td>
</tr>
</table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �o�^�t�H�[��
#-----------------------------------------------------------
sub data_new {
	my ($id,$nam,$eml,$memo) = @_;

	# �V�K�L���ǉ�
	if ($in{job} eq "new") {
		&data_add;
	}

	# �p�����[�^�w��
	my ($mode,$job);
	if ($in{data_new}) {
		$mode = "data_new";
		$job = "new";
	} else {
		$mode = "data_mente";
		$job = "edit2";
	}

	&header("���j���[TOP �� �o�^�t�H�[��");
	&back_btn;
	print <<EOM;
<b class="ttl">���o�^�t�H�[��</b>
<hr class="ttl" size="1">
<p>�e���ڂ���͂��đ��M�{�^���������Ă��������B</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="$mode" value="1">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="job" value="$job">
<table border="1" cellspacing="0" cellpadding="5" class="form">
<tr>
	<th>���O</th>
	<td><input type="text" name="name" size="40" value="$nam"></td>
</tr><tr>
	<th>E-mail</th>
	<td><input type="text" name="email" size="40" value="$eml"></td>
</tr><tr>
	<th>���[�U�[ID [�K�{]</th>
EOM

	# �V�K�t�H�[��
	if ($id eq "") {
		print qq|<td class="ttl"><input type="text" name="id" size="12" maxlength="8" style="ime-mode:inactive">\n|;
		print qq|�i�p����8�����ȓ��j</td></tr>\n|;
		print qq|<tr><th>�p�X���[�h [�K�{]</th>\n|;
  		print qq|<td class="ttl"><input type="text" name="pw" size="12" maxlength="8" style="ime-mode:inactive">\n|;
		print qq|�i�p����8�����ȓ��j</td></tr>\n|;

	# �C���t�H�[��
	} else {
		print qq|<td><b>$id</b></td></tr>\n|;
		print qq|<tr><th>�p�X���[�h</th>\n|;
  		print qq|<td class="ttl"><input type="text" name="pw" size="12" maxlength="8" style="ime-mode:inactive">\n|;
		print qq|�i�p����8�����ȓ��j<br>\n|;
		print qq|<input type="checkbox" name="pwchg" value="1"> �����ύX�̏ꍇ�̂݃`�F�b�N���A�V�p�X���[�h�����</td></tr>\n|;
		print qq|<input type="hidden" name="id" value="$in{id}">\n|;
	}

	print <<EOM;
<tr>
	<th>���l</th>
	<td><textarea name="memo" cols="42" rows="2">$memo</textarea></td>
</tr>
</table>
<br>
<input type="submit" value="���M����">
<input type="reset" value="���Z�b�g">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �f�[�^�ǉ�
#-----------------------------------------------------------
sub data_add {
	# �`�F�b�N
	if ($in{id} eq "" || $in{pw} eq "") {
		&error("ID�܂��̓p�X���[�h�������͂ł�");
	}
	if ($in{id} =~ /\W/ || $in{pw} =~ /\W/) {
		&error("ID�܂��̓p�X���[�h�ɉp�����ȊO�̕��������͂���Ă��܂�");
	}

	# �V�K���[�U�[�o�^
	my @regist_result = WebProtectAuth::create($in{id}, $in{pw}, $in{name}, $in{email}, $in{memo}, 0);
	if($regist_result[0] != WebProtectAuth::SUCCESS) {
		if($regist_result[0] == WebProtectAuth::ID_FILE_OPEN_ERROR) {
			&error("open err: $cf{pwdfile}");
		} elsif($regist_result[0] == WebProtectAuth::ID_EXISTS) {
			&error("<b>$in{id}</b>�͊��ɔ��s�ςł�");
		} elsif($regist_result[0] == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("write err: $cf{memfile}");
		}
	}

	$in{name}  ||= '���O�Ȃ�';
	$in{email} ||= 'E-mail�Ȃ�';
	$in{memo}  ||= '�Ȃ�';

	&header;
	print <<EOM;
<h4>���ȉ��̂Ƃ��蔭�s���܂����B</h4>
<dl>
<dt>�y���O�z<dd>$in{'name'}
<dt>�yE-mail�z<dd>$in{'email'}
<dt>�y���[�UID�z<dd>$in{'id'}
<dt>�y�p�X���[�h�z<dd>$in{'pw'}
<dt>�y���l�z<dd>$in{'memo'}
</dl>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="data_new" value="1">
<input type="submit" value="�o�^�t�H�[��">
</form>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="�Ǘ����j���[">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  ����o�^�����e�i���X
#-----------------------------------------------------------
sub data_mente {
	# --- �C���t�H�[��
	if ($in{job} eq "edit" && $in{id}) {

		# ����t�@�C���ǂݍ���
		my @read_result = WebProtectAuth::read($in{id});
		if($read_result[0] == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("open err: $cf{memfile}");
		} elsif($read_result[0]  == WebProtectAuth::ID_NOTFOUND) {
			&error("����t�@�C�� $cf{memfile} �� $in{id} ��������܂���ł����B");
		} else {
			shift(@read_result);
		}

		&data_new(@read_result);

	# --- �C�����s
	} elsif ($in{job} eq "edit2") {

		# �p�X���[�h�ύX
		if ($in{pwchg} == 1) {
			if ($in{pw} eq "" || $in{pw} =~ /\W/) {
				&error("�p�X���[�h�̎w�肪�s���ł�");
			}

			my $update_result = WebProtectAuth::update_password($in{id}, undef, $in{pw}, 1);
			if($update_result == WebProtectAuth::ID_FILE_OPEN_ERROR) {
				&error("open err: $cf{pwdfile}");
			}
		}

		# ����t�@�C��
		my $update_result = WebProtectAuth::update_userinfo($in{id}, $in{name}, $in{email}, $in{memo});
		if($update_result == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("open err: $cf{memfile}");
		}

		&msg_edit;

	# --- �폜
	} elsif ($in{job} eq "dele" && $in{id}) {

		# ���[�U�[�폜
		my $delete_result = WebProtectAuth::delete($in{id}, undef, 1);
		if($delete_result == WebProtectAuth::ID_FILE_OPEN_ERROR) {
			&error("open err: $cf{pwdfile}");
		} elsif($delete_result == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
			&error("open err: $cf{memfile}");
		}
	}

	# �y�[�W���F��
	$in{page} ||= 0;
	foreach ( keys(%in) ) {
		if (/^page:(\d+)$/) {
			$in{page} = $1;
			last;
		}
	}

	# ���[�U�[���я�
	foreach ( keys(%in) ) {
		if (/^desc:(\d+)$/) {
			$in{desc} = $1;
			last;
		}
	}
	if(!exists($in{desc})) { $in{desc} = 1; }

	&header("���j���[TOP �� ����o�^�����e�i���X");
	&back_btn;
	print <<EOM;
<form action="$cf{admin_cgi}" method="post" name="order">
<input type="hidden" name="data_mente" value="1">
<input type="hidden" name="pass" value="$in{pass}">
EOM
	print '<input type="hidden" name="desc" value="' . int(!$in{desc}) . "\">\n";
	print "<b class=\"ttl\">������o�^�����e�i���X</b>\n";
	print '<span style="margin-left:1em;"><a href="javascript:void(0)" onclick="javascript:order.submit()">[�o�^��' . ($in{desc} ? "��" : "�V��") . "�����ɕ��ёւ�]</a></span>\n";
	print <<EOM;
</form>
<hr class="ttl" size="1">
<p>������I�����đ��M�{�^���������Ă��������B</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_mente" value="1">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="page" value="$in{page}">
<input type="hidden" name="desc" value="$in{desc}">
���� : <select name="job">
<option value="edit">�C��
<option value="dele">�폜
</select>
<input type="submit" value="���M����">
EOM

	my @read_results = WebProtectAuth::multiread($in{page}, $in{desc});
	my $last;
	if($read_results[0] == WebProtectAuth::MEMBER_FILE_OPEN_ERROR) {
		&error("open err: $cf{memfile}");
	} else {
		shift(@read_results);
		$last = shift(@read_results);
	}

	for(my $i=0; $i<scalar(@read_results); $i++) {
		my ($id,$nam,$eml,$memo) = @{$read_results[$i]};

		$nam ||= '���O�Ȃ�';
		$eml ||= '���[���A�h���X�Ȃ�';
		$memo =~ s/<br>/ /g;

		print qq|<hr><input type="radio" name="id" value="$id">\n|;
		print qq|<b>$id</b> [���O] $nam [���l] $memo [���[��] $eml\n|;
	}

	print "<hr>\n";

	my $next = $in{page} + $cf{pg_max};
	my $back = $in{page} - $cf{pg_max};
	if ($back >= 0) {
		print qq|<input type="submit" name="page:$back" value="�O��$cf{pg_max}��">\n|;
	}
	if ($next < $last) {
		print qq|<input type="submit" name="page:$next" value="����$cf{pg_max}��">\n|;
	}

	print "</form>\n";
	print "</body></html>\n";
	exit;
}

#-----------------------------------------------------------
#  ���O�{��
#-----------------------------------------------------------
sub look_log {
	if (!$in{list} && !$in{calc}) { $in{list} = 1; }
	my %btn = ('list' => '�ꗗ', 'calc' => '�W�v');

	&header("���j���[TOP �� �A�N�Z�X���O�{��");
	&back_btn;
	print <<EOM;
<b class="ttl">���A�N�Z�X���O�{��</b>
<hr class="ttl" size="1">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="look_log" value="1">
EOM

	foreach ( 'list', 'calc' ) {
		if ($in{$_}) {
			print qq|<input type="submit" name="$_" value="$btn{$_}" disabled>\n|;
		} else {
			print qq|<input type="submit" name="$_" value="$btn{$_}">\n|;
		}
	}

	print "</form>\n";

	# ���O�ꗗ�̏ꍇ
	if ($in{list}) {
		print "<dl><dt>��<b>���O�ꗗ</b>\n";

		open(IN,"$cf{logfile}") || &error("Open Err: $cf{logfile}");
		while (<IN>) {
			my ($id,$date,$host,$agent) = split(/<>/);

			print "<dt><hr><b>$id</b> - $date �y$host�z\n";
			print "<dd>$agent\n";
		}
		close(IN);

		print "<dt><hr></dl>\n";

	# ���O�W�v�̏ꍇ
	} else {
		my ($i, %log);
		open(IN,"$cf{logfile}") || &error("Open Err: $cf{logfile}");
		while (<IN>) {
			my ($id,$date,$host,$agent) = split(/<>/);

			$log{$id}++;
			$i++;
		}
		close(IN);

		print qq|<p>��<b>���O�W�v</b> (���� : $i��)</p>\n|;
		print qq|<table border="1" cellpadding="3" cellspacing="0" class="form">\n|;
		print qq|<tr><th>���[�UID</th>\n|;
		print qq|<th>�A�N�Z�X��</th></tr>\n|;

		# �\�[�g
		foreach ( sort { $log{$b} <=> $log{$a} }keys(%log) ) {
			print qq|<tr><td nowrap>$_<br></td>\n|;
			print qq|<td align="center">$log{$_}</td></tr>\n|;
		}
		print "</table>\n";
	}

	print "</body></html>\n";
	exit;
}

#-----------------------------------------------------------
#  �Z�b�V�����t�@�C���|��
#-----------------------------------------------------------
sub exp_ses {
	# ���s
	if ($in{submit}) {
		# �`�F�b�N
		$in{delta} =~ s/\D//g;
		if ($in{delta} eq '') { &error("���Ԑ��̎w�肪�s���ł��B���p�����Ŏw�肵�Ă��������B"); }

		# �b���ɒ���
		$in{delta} *= 60;

		# �����؂�t�@�C�����폜
		CGI::Session::ExpireSessions -> new(temp_dir => $cf{sesdir}, delta => $in{delta}) -> expire_file_sessions();

		# �������
		&msg_expses;
	}

	# �f�t�H���g
	my $delta = $cf{job_time} + 10;

	&header("���j���[TOP �� �Z�b�V�����t�@�C���|��");
	&back_btn;
	print <<EOM;
<b class="ttl">���Z�b�V�����t�@�C���|��</b>
<hr class="ttl" size="1">
<p>
	���p�҂����O�C����A���O�A�E�g�����Ƀu���E�U�����ƁA�s�v�ȃZ�b�V�����t�@�C�����~�ς���܂��B<br>
	����I�ɁA�s�v�ȃZ�b�V�����t�@�C����|������悤�ɂ��܂��傤�B<br>
</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="exp_ses" value="1">
<table border="1" cellspacing="0" cellpadding="5" class="form">
<tr>
	<th>���X�V�t�@�C���F</th>
	<td nowrap>
		<input type="text" name="delta" size="5" value="$delta"> ���ȏ�̂��̂��폜<br>
		�i���O�C���F�،�̐ݒ莞��<b>$cf{job_time}</b>���ȏ�Őݒ肷�邱�Ɓj
	</td>
</tr>
</table>
<br>
<input type="submit" name="submit" value=" ���s���� ">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �p�X���[�h�F��
#-----------------------------------------------------------
sub check_passwd {
	# �p�X���[�h�������͂̏ꍇ�͓��̓t�H�[�����
	if ($in{pass} eq "") {
		&enter_form;

	# �p�X���[�h�F��
	} elsif ($in{pass} ne $cf{password}) {
		&error("�F�؂ł��܂���");
	}
}

#-----------------------------------------------------------
#  �������
#-----------------------------------------------------------
sub enter_form {
	&header("�������");
	print <<EOM;
<div align="center">
<form action="$cf{admin_cgi}" method="post">
<table width="380" style="margin-top:70px;">
<tr>
	<td height="40" align="center">
		<fieldset><legend>�Ǘ��p�X���[�h����</legend>
		<br>
		<input type="password" name="pass" value="" size="20">
		<input type="submit" value=" �F�� ">
		<br><br>
		</fieldset>
	</td>
</tr>
</table>
</form>
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �߂�{�^��
#-----------------------------------------------------------
sub back_btn {
	print <<EOM;
<div align="right">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="&lt; ���j���[">
</form>
</div>
EOM
}

#-----------------------------------------------------------
#  �C���������b�Z�[�W
#-----------------------------------------------------------
sub msg_edit {
	&header("�C������");
	print <<EOM;
<b class="ttl">���C������</b>
<hr class="ttl" size="1">
<h4>�C�����������܂���</h4>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="data_mente" value="1">
<input type="submit" value="�����e�i���X���" style="width:150px;">
</form>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="�Ǘ����j���[" style="width:150px;">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �������b�Z�[�W
#-----------------------------------------------------------
sub msg_expses {
	&header("�|������");
	print <<EOM;
<b class="ttl">���|������</b>
<hr class="ttl" size="1">
<h4>�s�v�ȃZ�b�V�����t�@�C���̍폜���������܂���</h4>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="�Ǘ����j���[" style="width:100px;">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  HTML�w�b�_
#-----------------------------------------------------------
sub header {
	my $ttl = shift;

	print "Content-type: text/html\n\n";
	print <<EOM;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,th,td { font-size:80%; background:#fff; }
.ttl { color:green; }
.msg { background:#ddd; }
table.form th { background:#ccc; white-space:nowrap; }
-->
</style>
<title>$ttl</title>
</head>
<body>
EOM
}