#!/usr/local/bin/perl

#������������������������������������������������������������
#�� WEB PROTECT : manager.cgi - 2011/10/02
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#������������������������������������������������������������

our %cf;
BEGIN {
	# �ݒ�t�@�C����荞��
	require './init.cgi';
	%cf = &init;
}

use strict;
use CGI::Carp qw(fatalsToBrowser);
use Encode qw();
use File::Basename;
use File::Spec;
use JSON::XS;
use lib qq($main::cf{webpatio_lib_path});
use HistoryCookie;
use UniqueCookie;

# �f�[�^��
my %in = &parse_form;

# ��������
if ($in{mode} eq "new_user") { &new_user; }
if ($in{mode} eq "chg_pwd") { &chg_pwd; }
&error("�s���ȃA�N�Z�X�ł�");

#-----------------------------------------------------------
#  ���[�U�o�^
#-----------------------------------------------------------
sub new_user {
	my ($regist_log_fh, $pwd_fh, $mem_fh, $history_log_folder_number_log_fh, $history_logfile_count_log_fh, $history_log_fh);
	my @opened_fh;

	# ���s����
	if ($cf{pwd_regist} > 1) { &error("�s���ȃA�N�Z�X�ł�"); }

	# �`�F�b�N
	my $err;
	if (length($in{id}) < 4 || length($in{id}) > 8) {
		$err .= "����ID��4�`8�����œ��͂��Ă�������<br>";
	}
	if ($in{id} =~ /\W/) {
		$err .= "����ID�ɉp�����ȊO�̕������܂܂�Ă��܂�<br>";
	}
	if ($err) { &error($err); }

	# �����擾
	my ($time) = get_time();

	# �z�X�g�����擾
	my ($host,$addr) = &get_host;
	&deny_host($host,$addr);

	# �S�Ă�Cookie���擾
	my %cookies;
	foreach my $set (split(/; */, $ENV{'HTTP_COOKIE'})) {
		my ($key, $val) = split(/=/, $set);
		$cookies{$key} = $val;
	}

	# ���j�[�NCookieA���擾
	my $cookie_a = do {
		my $instance = UniqueCookie->new($cf{webpatio_cookie_current_dirpath});
		$instance->value() || '-';
	};

	# �o�^ID���擾
	my $user_id_on_cookie = do {
		# �f�[�^��URL�f�R�[�h���ĕ���
		my $cookie_name = "WEB_PATIO_$cf{webpatio_cookie_current_dirpath}";
		my @webpatio_cookie;
		foreach my $val (split(/<>/, $cookies{$cookie_name})) {
			$val =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
			push(@webpatio_cookie, $val);
		}
		$webpatio_cookie[5] || '-';
	};

	# ����ID���擾
	my $history_cookie = HistoryCookie->new();
	my $chistory_id = $history_cookie->get_history_id();

	# �A������ID���s�`�F�b�N
	my $repeatitive_regist_boundary_time = $time - $cf{wait_regist};
	my $is_exempt_host = scalar(grep { index($host, $_) != -1 } @{$cf{wait_regist_exempt_hosts}}) > 0; # ���O�z�X�g���ǂ���
	if (!open($regist_log_fh, '+<', $cf{regist_log})) {
		close($_) foreach @opened_fh;
		&error("open err: $cf{regist_log}");
	}
	push(@opened_fh, $regist_log_fh);
	if (!flock($regist_log_fh, 2)) {
		close($_) foreach @opened_fh;
		&error("lock err: $cf{regist_log}");
	}
	seek($regist_log_fh, 0, 0);
	while (<$regist_log_fh>) {
		# �����v�t���b�O
		my $flg = 0;

		# ���O�s�ǂݎ��
		my ($r_host, $r_cookie_a, $r_user_id, $r_history_id, $r_time) = split(/<>/);
		# �A�����s�������ԓ��łȂ���΃X�L�b�v
		if ($r_time < $repeatitive_regist_boundary_time) {
			next;
		}
		# �z�X�g��v����
		$flg ||= !$is_exempt_host && $r_host eq $host;
		# CookieA��v����
		$flg ||= $r_cookie_a ne '-' && $r_cookie_a eq $cookie_a;
		# �o�^ID��v����
		$flg ||= $r_user_id ne '-' && $r_user_id eq $user_id_on_cookie;
		# ����ID��v����
		$flg ||= defined($chistory_id) && $r_history_id eq $chistory_id;

		# �����ꂩ�̔���ň�v�����ꍇ
		if ($flg) {
			close($_) foreach @opened_fh;
			&error('�A���o�^�͂������΂炭���Ԃ������ĉ�����');
		}
	}

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
			&error("���Ɏg�p����Ă��鏑��ID�ł�");
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
		if ($read_line ne '') {
			$read_line;
		} else {
			truncate($history_log_folder_number_log_fh, 0);
			seek($history_log_folder_number_log_fh, 0, 0);
			print $history_log_folder_number_log_fh "01";
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
		if ($read_logfile_count eq '') {
			# �������O�ۑ��t�H���_���������O�����O�t�@�C�� �V�K�쐬����0�Ƃ���
			truncate($history_logfile_count_log_fh, 0);
			seek($history_logfile_count_log_fh, 0, 0);
			print $history_logfile_count_log_fh "0";
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
		print $history_log_folder_number_log_fh "$history_log_folder_number_str";

		# �������O�ۑ��t�H���_���������O���J�E���g�����������āA���O�t�@�C���ɕۑ�
		$history_logfile_count = 0;
		truncate($history_logfile_count_log_fh, 0);
		seek($history_logfile_count_log_fh, 0, 0);
		print $history_logfile_count_log_fh "$history_logfile_count";
	}

	# ID���s
	my $id = "${history_log_folder_number_str}_$in{id}";

	# �p�X���s
	my @char = (0 .. 9, 'a' .. 'z', 'A' .. 'Z');
	my $pw;
	srand;
	foreach (1 .. 8) {
		$pw .= $char[int(rand(@char))];
	}

	# �������O�ۑ��t�H���_��K�v�ɉ����č쐬
	my $save_history_dir = File::Spec->catfile(File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/' . $cf{history_logdir})), $history_log_folder_number_str);
	if (!-d $save_history_dir) {
		if (!mkdir($save_history_dir)) {
			close($_) foreach @opened_fh;
			error("Create Error: HistoryLog SaveFolder");
		}
	}

	# Cookie�ɕۑ����Ă����e��ݒ��ǂݎ��A����ID���O�ɋL�^
	# ����ID���O�t�@�C���I�[�v��
	if (!open($history_log_fh, '>', File::Spec->catfile($save_history_dir, "$id.log"))) {
		close($_) foreach @opened_fh;
		error("Open Error: HistoryLog");
	}
	push(@opened_fh, $history_log_fh);
	if (!flock($history_log_fh, 6)) {
		# �����̃v���Z�X���炱�̉ӏ��œ����I�[�v�����邱�Ƃ͂Ȃ��̂ŁA
		# ���b�N���m����0��Ԃ�
		close($_) foreach @opened_fh;
		error("Lock Error: HistoryLog");
	}
	# ���݂���R�s�[�Ώۂ�Cookie�ݒ��ǂݎ��AJSON���\�z
	my $json = JSON::XS->new();
	my %copy_settings;
	## ����������҂���ݒ�l�̃R�s�[
	foreach my $cookie_suffix ('NGThread', 'NGID_LIST', 'NGNAME_LIST', 'NGWORD_LIST') {
		my $cookie_name = "WEB_PATIO_$cf{webpatio_cookie_current_dirpath}_$cookie_suffix";
		if (exists($cookies{$cookie_name}) && $cookies{$cookie_name} ne '') {
			my $load_value = do {
				my $urldecoded_value = $cookies{$cookie_name};
				$urldecoded_value =~ s/\+/ /g;
				$urldecoded_value =~ s/%([0-9a-fA-F]{2})/pack("H2", $1)/eg;
				$urldecoded_value = Encode::decode('UTF-8', $urldecoded_value);
				$json->utf8(0)->decode($urldecoded_value);
			};
			$copy_settings{$cookie_suffix} = $load_value;
		}
	}
	## ���l�ɂ��t���O(0/1)�����҂���ݒ�l�̃R�s�[
	foreach my $cookie_suffix ('CHAIN_NG', 'HIGHLIGHT_NAME') {
		my $cookie_name = "WEB_PATIO_$cf{webpatio_cookie_current_dirpath}_$cookie_suffix";
		if (exists($cookies{$cookie_name}) && ($cookies{$cookie_name} eq '0' || $cookies{$cookie_name} eq '1')) {
			$copy_settings{$cookie_suffix} = int($cookies{$cookie_name});
		}
	}

	# ����ID���O�t�@�C���ɏ�������
	print $history_log_fh $json->utf8(1)->encode(\%copy_settings);

	# �������O�ۑ��t�H���_���������O�����J�E���g�A�b�v
	$history_logfile_count++;

	# �������O�ۑ��t�H���_���������O�������O�t�@�C���ɕۑ�
	truncate($history_logfile_count_log_fh, 0);
	seek($history_logfile_count_log_fh, 0, 0);
	print $history_logfile_count_log_fh "$history_logfile_count";

	# �p�X���[�h�t�@�C�� ���[�U�[�s�쐬
	my $crypt = encrypt($pw); # �p�X���[�h�Í���
	my $hash = saltedhash_encrypt("$id$pw"); # �n�b�V�����쐬
	push(@data,"$id:$crypt:$hash\n");

	# �p�X���[�h�t�@�C���X�V
	seek($pwd_fh, 0, 0);
	print $pwd_fh @data;
	truncate($pwd_fh, tell($pwd_fh));

	# ����t�@�C���X�V
	print $mem_fh "$id<><><><>\n";

	# ����ID���s���O�t�@�C���X�V
	seek($regist_log_fh, 0, 0);
	my @regist_log_write_tmp = ("$host<>$cookie_a<>$user_id_on_cookie<>$id<>$time<>\n");
	while (<$regist_log_fh>) {
		my $r_time = (split(/<>/))[4];
		if ($r_time < $repeatitive_regist_boundary_time) {
			last;
		}
		push(@regist_log_write_tmp, $_);
	}
	seek($regist_log_fh, 0, 0);
	print $regist_log_fh @regist_log_write_tmp;
	truncate($regist_log_fh, tell($regist_log_fh));

	# �e�t�@�C���n���h���N���[�Y
	close($_) foreach @opened_fh;

	# ���s�������Ƀ��O�C��
	$history_cookie->login($id, $pw);

	# �������
	my $msg = qq|����ID�Ɨ����p�X���[�h�𔭍s���܂����B<br><br>����ID�F$id<br>�p�X���[�h�F$pw|;
	&message("����ID�E�����p�X���[�h���s����", $msg);
}

#-----------------------------------------------------------
#  ���[�UPW�ύX
#-----------------------------------------------------------
sub chg_pwd {
	# ���s����
	if ($cf{pwd_regist} > 2) { &error("�s���ȃA�N�Z�X�ł�"); }

	# �z�X�g�����擾
	my ($host,$addr) = &get_host;
	&deny_host($host,$addr);

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

	# �`�F�b�N
	my $err;
	if ($login_id eq "") { $err .= "����ID�����̓����ł�<br>"; }
	if ($in{pw} eq "") { $err .= "���p�X���[�h�����̓����ł�<br>"; }
	if ($in{pw1} eq "") { $err .= "�V�p�X���[�h�����̓����ł�<br>"; }
	if ($in{pw1} ne $in{pw2}) { $err .= "�V�p�X���[�h�ōēx���͕����قȂ�܂�<br>";	}
	if (length($in{pw1}) > 8) { $err .= "�V�p�X���[�h��8�����ȓ��ł�<br>"; }
	if ($in{pw1} =~ /[^\w_]/) { $err .= "�p�X���[�h�͉p������_(�A���_�[�X�R�A)�̂ݎg�p�\�ł�<br>"; }
	if ($err) { &error($err); }

	# ID�`�F�b�N
	my ($flg, $new_user_hash, @data);
	open(DAT,"+< $cf{pwdfile}") or &error("open err: $cf{pwdfile}");
	flock(DAT, 2) or &error("lock err: $cf{pwdfile}");
	while (<DAT>) {
		my ($id,$crypt) = split(/:/);

		if ($login_id eq $id) {
			$flg++;
			# �ƍ�
			chomp($crypt);
			if ($in{pw} ne decrypt($crypt)) {
				close(DAT);
				&error("�F�؂ł��܂���");
			}
			$new_user_hash = saltedhash_encrypt("$id$in{pw1}");
			$_ = "$id:" . encrypt($in{pw1}) . ":$new_user_hash\n";
		}
		push(@data,$_);
	}

	if (!$flg) {
		close(DAT);
		&error("�F�؂ł��܂���");
	}

	# �p�X�t�@�C���X�V
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	# �X�V�������ōēx���O�C��
	my $history_cookie = HistoryCookie->new();
	$history_cookie->logout();
	$history_cookie->login($login_id, $in{pw1});

	# �������
	&message("�����p�X���[�h�ύX����", "�����p�X���[�h��ύX���܂����B");
}

#-----------------------------------------------------------
#  �A�N�Z�X����
#-----------------------------------------------------------
sub deny_host {
	my ($host,$addr) = @_;

	my $flg;
	foreach ( split(/\s+/, $cf{deny}) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;
		if ($host =~ /$_/i || $addr =~ /$_/i) {
			$flg++;
			last;
		}
	}
	if ($flg) { &error("���ݓo�^�x�~���ł�"); }
}
