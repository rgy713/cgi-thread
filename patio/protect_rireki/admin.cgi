#!/usr/local/bin/perl

#������������������������������������������������������������
#�� WEB PROTECT : admin.cgi - 2013/04/06
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);
use File::Spec;
use File::Basename;
use lib "./lib";
use Jcode;

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
	<td>����ID���s</td>
</tr><tr>
	<th><input type="submit" name="data_mente" value="�I��"></th>
	<td>����ID�����e�i���X�i�C���E�폜�j</td>
</tr><tr>
	<th><input type="submit" name="look_log" value="�I��"></th>
	<td>�A�N�Z�X���O�{��</td>
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
	<th>����ID [�K�{]</th>
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
	<th>���O</th>
	<td><input type="text" name="name" size="40" value="$nam"></td>
</tr>
<tr>
	<th>E-mail</th>
	<td><input type="text" name="email" size="40" value="$eml"></td>
</tr>
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
	my ($pwd_fh, $mem_fh, $history_log_folder_number_log_fh, $history_logfile_count_log_fh);
	my @opened_fh;

	# �`�F�b�N
	my $err;
	if ($in{id} eq "") {
		$err .= "����ID�������͂ł�<br>";
	} else {
		if (length($in{id}) < 4 || length($in{id}) > 8) {
			$err .= "����ID��4�`8�����œ��͂��Ă�������<br>";
		}
		if ($in{id} =~ /\W/) {
			$err .= "����ID�ɉp�����ȊO�̕������܂܂�Ă��܂�<br>";
		}
	}
	if ($in{pw} eq "") {
		$err .= "�p�X���[�h�������͂ł�<br>";
	} else {
		if ($in{pw} =~ /[^\w_]/) {
			$err .= "�p�X���[�h�ɉp������_(�A���_�[�X�R�A)�ȊO�̕������܂܂�Ă��܂�<br>";
		}
	}
	if ($err) { &error($err); }

	# �p�X���[�h�t�@�C���I�[�v��
	if (!open($pwd_fh, '+<', $cf{pwdfile})) {
		close($_) foreach @opened_fh;
		&error("open err: $cf{pwdfile}");
	}
	push(@opened_fh, $pwd_fh);
	if (!flock($pwd_fh, 2)) {
		close($_) foreach @opened_fh;
		&error("lock err: $cf{pwdfile}");
	}

	# ID�̏d���`�F�b�N
	my @data;
	while (<$pwd_fh>) {
		my ($r_history_id) = split(/:/);

		# ID�擪�̕����t�H���_�i���o�[������菜��
		$r_history_id =~ s/^[0-9][0-9]_//o;

		if ($in{id} eq $r_history_id) {
			close($_) foreach @opened_fh;
			&error("<b>$in{id}</b>�͊��ɔ��s�ςł�");
		}
		push(@data,$_);
	}

	# ����t�@�C���I�[�v��
	if (!open($mem_fh, '>>', $cf{memfile})) {
		close($_) foreach @opened_fh;
		&error("write err: $cf{memfile}");
	}
	push(@opened_fh, $mem_fh);
	if (!flock($mem_fh, 2)) {
		close($_) foreach @opened_fh;
		&error("lock err: $cf{memfile}");
	}

	# �������O�����ۑ��t�H���_�ԍ����O�t�@�C���I�[�v��
	if (!open($history_log_folder_number_log_fh, '+>>', $cf{history_logdir_number})) {
		close($_) foreach @opened_fh;
		error('Open Error: HistoryLog SaveFolderNumber Log');
	}
	push(@opened_fh, $history_log_folder_number_log_fh);
	if (!flock($history_log_folder_number_log_fh, 2)) {
		close($_) foreach @opened_fh;
		error('Lock Error: HistoryLog SaveFolderNumber Log');
	}
	seek($history_log_folder_number_log_fh, 0, 0);

	# �������O�����ۑ��t�H���_�ԍ��ǂݎ��
	my $history_log_folder_number_str = do {
		my $read_line = <$history_log_folder_number_log_fh>;
		chomp($read_line);
		if ($read_line ne '') {
			$read_line;
		} else {
			truncate($history_log_folder_number_log_fh, 0);
			seek($history_log_folder_number_log_fh, 0, 0);
			print $history_log_folder_number_log_fh "01\n";
			'01';
		}
	};

	# �������O�ۑ��t�H���_���������O�����O�t�@�C�����I�[�v��
	if (!open($history_logfile_count_log_fh, '+>>', $cf{history_logfile_count})) {
		close($_) foreach @opened_fh;
		error("Open Error: HistoryLog Count Log");
	}
	push(@opened_fh, $history_logfile_count_log_fh);
	if (!flock($history_logfile_count_log_fh, 2)) {
		close($_) foreach @opened_fh;
		error("Lock Error: HistoryLog Count Log");
	}
	seek($history_logfile_count_log_fh, 0, 0);

	# �������O�ۑ��t�H���_���������O����ǂݎ��
	my $history_logfile_count = do {
		my $read_logfile_count = <$history_logfile_count_log_fh>;
		chomp($read_logfile_count);
		if ($read_logfile_count eq '') {
			# �������O�ۑ��t�H���_���������O�����O�t�@�C�� �V�K�쐬����0�Ƃ���
			truncate($history_logfile_count_log_fh, 0);
			seek($history_logfile_count_log_fh, 0, 0);
			print $history_logfile_count_log_fh "0\n";
			0;
		} else {
			# �������O�ۑ��t�H���_���������O����ǂݎ��
			int($read_logfile_count);
		}
	};
	if ($history_logfile_count >= $cf{number_of_logfile_in_history_logdir}) {
		# �������O�ۑ��t�H���_���������O��������߂̏ꍇ�A
		# �������O�����ۑ��t�H���_�ԍ����J�E���g�A�b�v���āA���O�t�@�C���ɕۑ�
		my $new_history_log_folder_number = int($history_log_folder_number_str) + 1;
		if ($new_history_log_folder_number > 99) {
			$new_history_log_folder_number = 1;
		}
		$history_log_folder_number_str = sprintf('%02d', $new_history_log_folder_number);
		truncate($history_log_folder_number_log_fh, 0);
		seek($history_log_folder_number_log_fh, 0, 0);
		print $history_log_folder_number_log_fh "$history_log_folder_number_str\n";

		# �������O�ۑ��t�H���_���������O���J�E���g�����������āA���O�t�@�C���ɕۑ�
		$history_logfile_count = 0;
		truncate($history_logfile_count_log_fh, 0);
		seek($history_logfile_count_log_fh, 0, 0);
		print $history_logfile_count_log_fh "$history_logfile_count\n";
	}

	# �������O�ۑ��t�H���_��K�v�ɉ����č쐬
	{
		my $save_history_dir = File::Spec->catfile(File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/' . $cf{history_logdir})), $history_log_folder_number_str);
		if (!-d $save_history_dir) {
			if (!mkdir($save_history_dir)) {
				close($_) foreach @opened_fh;
				error("Create Error: HistoryLog SaveFolder");
			}
		}
	}

	# �������O�ۑ��t�H���_���������O�����J�E���g�A�b�v
	$history_logfile_count++;

	# �������O�ۑ��t�H���_���������O�������O�t�@�C���ɕۑ�
	truncate($history_logfile_count_log_fh, 0);
	seek($history_logfile_count_log_fh, 0, 0);
	print $history_logfile_count_log_fh "$history_logfile_count\n";

	# ID���s
	my $id = "${history_log_folder_number_str}_$in{id}";

	# �p�X���[�h�t�@�C�� ���[�U�[�s�쐬
	my $crypt = encrypt($in{pw}); # �p�X���[�h�Í���
	my $hash = saltedhash_encrypt("$id$in{pw}"); # �n�b�V���쐬
	push(@data,"$id:$crypt:$hash\n");

	# �p�X���[�h�t�@�C���X�V
	seek($pwd_fh, 0, 0);
	print $pwd_fh @data;
	truncate($pwd_fh, tell($pwd_fh));

	# ����t�@�C���X�V
	print $mem_fh "$id<><><>$in{memo}<>\n";

	# �e�t�@�C���n���h���N���[�Y
	close($_) foreach @opened_fh;

	$in{name}  ||= '���O�Ȃ�';
	$in{name}  ||= 'E-mail�Ȃ�';
	$in{memo}  ||= '�Ȃ�';

	&header;
	print <<EOM;
<h4>���ȉ��̂Ƃ��蔭�s���܂����B</h4>
<dl>
<dt>�y����ID�z<dd>$id
<dt>�y�����p�X���[�h�z<dd>$in{'pw'}
<dt>�y���O�z<dd>$in{'name'}
<dt>�yE-mail�z<dd>$in{'email'}
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

		# ����t�@�C��
		my @log;
		open(IN,"$cf{memfile}") or &error("open err: $cf{memfile}");
		while (<IN>) {
			my ($id,$nam,$eml,$memo) = split(/<>/);

			if ($in{id} eq $id) {
				@log = ($id,$nam,$eml,$memo);
				last;
			}
		}
		close(IN);

		&data_new(@log);

	# --- �C�����s
	} elsif ($in{job} eq "edit2") {

		# �p�X���[�h�ύX
		if ($in{pwchg} == 1) {
			my $err;
			if ($in{pw} eq "") {
				$err .= "�p�X���[�h�������͂ł�<br>";
			} else {
				if ($in{pw} =~ /\W/) {
					$err .= "�p�X���[�h�ɉp�����ȊO�̕������܂܂�Ă��܂�<br>";
				}
			}
			if ($err) { &error($err); }

			# �p�X���[�h�t�@�C��
			my @data;
			open(DAT, '+<', $cf{pwdfile}) or &error("open err: $cf{pwdfile}");
			flock(DAT, 2) or &error("lock err: $cf{pwdfile}");
			while (<DAT>) {
				my ($id,$pw) = split(/:/);
				if ($in{id} eq $id) {
					my $crypt = encrypt($in{pw}); # �p�X���[�h�Í���
					my $hash = saltedhash_encrypt("$id$in{pw}"); # �n�b�V���쐬
					$_ = "$in{id}:$crypt:$hash\n";
				}
				push(@data,$_);
			}
			seek(DAT, 0, 0);
			print DAT @data;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

		# ����t�@�C��
		my @data;
		open(DAT,"+< $cf{memfile}") or &error("open err: $cf{memfile}");
		flock(DAT, 2) or &error("lock err: $cf{memfile}");
		while (<DAT>) {
			my ($id,$nam,$eml,$memo) = split(/<>/);

			if ($in{id} eq $id) {
				$_ = "$id<>$in{name}<>$in{email}<>$in{memo}<>\n";
			}
			push(@data,$_);
		}
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		&msg_edit;

	# --- �폜
	} elsif ($in{job} eq "dele" && $in{id}) {

		# �p�X���[�h�t�@�C��
		my @data;
		open(DAT,"+< $cf{pwdfile}") or &error("open err: $cf{pwdfile}");
		flock(DAT, 2) or &error("lock err: $cf{pwdfile}");
		while (<DAT>) {
			my ($id,$pw) = split(/:/);
			next if ($in{id} eq $id);

			push(@data,$_);
		}
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# ����t�@�C��
		@data = ();
		open(DAT,"+< $cf{memfile}") or &error("open err: $cf{memfile}");
		flock(DAT, 2) or &error("lock err: $cf{memfile}");
		while (<DAT>) {
			my ($id,$nam,$eml,$memo) = split(/<>/);
			next if ($in{id} eq $id);

			push(@data,$_);
		}
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);
	}

	# �y�[�W���F��
	$in{page} ||= 0;
	foreach ( keys(%in) ) {
		if (/^page:(\d+)$/) {
			$in{page} = $1;
			last;
		}
	}

	&header("���j���[TOP �� ����ID�����e�i���X");
	&back_btn;
	print <<EOM;
<b class="ttl">������ID�����e�i���X</b>
<hr class="ttl" size="1">
<p>������I�����đ��M�{�^���������Ă��������B</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_mente" value="1">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="page" value="$in{page}">
���� : <select name="job">
<option value="edit">�C��
<option value="dele">�폜
</select>
<input type="submit" value="���M����">
EOM

	my $i = 0;
	open(IN,"$cf{memfile}") or &error("open err: $cf{memfile}");
	flock(IN, 1)  or &error("lock err: $cf{memfile}");
	while (<IN>) {
		$i++;
		next if ($i < $in{page} + 1);
		next if ($i > $in{page} + $cf{pg_max});

		my ($id,$nam,$eml,$memo) = split(/<>/);
		$nam ||= '���O�Ȃ�';
		$eml &&= "<a href=\"mailto:$eml\">$nam</a>";
		$memo =~ s/<br>/ /g;

		print qq|<hr><input type="radio" name="id" value="$id">\n|;
		print qq|<b>$id</b> [���O] $nam [���l] $memo\n|;
	}
	close(IN);

	print "<hr>\n";

	my $next = $in{page} + $cf{pg_max};
	my $back = $in{page} - $cf{pg_max};
	if ($back >= 0) {
		print qq|<input type="submit" name="page:$back" value="�O��$cf{pg_max}��">\n|;
	}
	if ($next < $i) {
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