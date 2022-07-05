# �p�b�P�[�W���錾
package WebProtectAuth;

# ���W���[���錾
use strict;
use File::Basename qw/dirname/;
use File::Spec;
use File::ReadBackwards;

# WebProtect�f�B���N�g�� ���s�p�X����̑��΃p�X�擾
my $basedir = File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/../'));

# �ݒ�t�@�C����荞��
require "$basedir/init.cgi";
my %cf = &init;

# ���O�p�X��WebProtect���΃p�X�ɒu��
my @path_replace = ('pwdfile','memfile','regist_log');
for my $key (@path_replace) {
	if(!File::Spec->file_name_is_absolute($cf{$key})) {
		$cf{$key} = File::Spec->canonpath("$basedir/$cf{$key}");
	}
}

# �������ʒ萔��`
use constant {
	SUCCESS                     =>  0,
	ID_FILE_OPEN_ERROR          =>  1,
	MEMBER_FILE_OPEN_ERROR      =>  1 << 1,
	REGIST_LOG_FILE_OPEN_ERROR  =>  1 << 2,
	IS_DENY_HOST                =>  1 << 3,
	ID_NOTFOUND                 =>  1 << 4,
	PASS_MISMATCH               =>  1 << 5,
	ID_EXISTS                   =>  1 << 6,
	REPEATITIVE_REGIST_LIMIT    =>  1 << 7,
	DUPLICATE_EMAIL_ADDRESS     =>  1 << 8,
	IS_DENY_EMAIL_ADDRESS       =>  1 << 9
};

# ���[�U�o�^�A�N�Z�X�����z�X�g�ł��邩�ǂ���(�v���C�x�[�g�֐�)
my $isDenyHost = sub {
	shift;
	my ($host,$addr) = @_;

	foreach ( split(/\s+/, $cf{deny}) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;
		if ($host =~ /$_/i || $addr =~ /$_/i) {
			return 1;
		}
	}

	return 0;
};

# �֎~���[�h���܂ރ��[���A�h���X�ł��邩�ǂ���(�v���C�x�[�g�֐�)
my $isDenyEMailAddress = sub {
	shift;
	my ($eml) = @_;
	my @deny_words = split(/,/, $cf{deny_email});

	for my $word (@deny_words) {
		if($eml =~ /\Q$word/i) {
			return 1;
		}
	}

	return 0;
};

# ���[�U�[�F��
sub authenticate {
	my ($id,$pw) = @_;

	# �p�X�t�@�C���I�[�v��
	my $crypt;
	open(IN,"$cf{pwdfile}") or return ID_FILE_OPEN_ERROR;
	while (<IN>) {
		my ($r_id,$r_pw) = split(/:/);

		if ($r_id eq $id) {
			$crypt = $r_pw;
			last;
		}
	}
	close(IN);

	# ID�s��v�̏ꍇ
	chomp($crypt);
	if (!$crypt) { return ID_NOTFOUND; }

	# �ƍ�����
	if (&decrypt($pw, $crypt) != 1) { return PASS_MISMATCH; }
	
	# �F�ؐ���
	return SUCCESS;
}

# �V�K���[�U�[�o�^
sub create {
	my ($id,$pw,$name,$eml,$memo,$notadmin_regist) = @_;
	my ($host,$addr) = &get_host;
	my ($time,$date) = &get_time;
	my $repeatitive_regist_boundary_time = $time - $cf{wait_regist};

	# ���[�U�[�o�^�����z�X�g�`�F�b�N
	if($pw eq "" && self->$isDenyHost($host,$addr)) { return IS_DENY_HOST; }

	# �A���V�K���[�U�[�o�^�`�F�b�N
	if($notadmin_regist == 1) {
		open(REGISTLOG,"< $cf{regist_log}") or return REGIST_LOG_FILE_OPEN_ERROR;
		while (<REGISTLOG>) {
			my ($r_host,$r_time) = split(/<>/);
			if ($r_host eq $host && $r_time >= $repeatitive_regist_boundary_time) {
				close(REGISTLOG);
				return REPEATITIVE_REGIST_LIMIT;
			}
		}
		close(REGISTLOG);
	}

	# �֎~���[�h���܂ރ��[���A�h���X�ł��邩�ǂ����`�F�b�N
	if($notadmin_regist == 1 && self->$isDenyEMailAddress($eml)) { return IS_DENY_EMAIL_ADDRESS; }

	# �R�[�h�ϊ�
	Jcode::convert($name, 'sjis');

	# ����t�@�C�� ID�E���[���A�h���X�̏d���`�F�b�N
	my @data = ("$id<>$name<>$eml<>$memo<>\n");
	my $flg = SUCCESS;
	open(DAT,"+< $cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	while (<DAT>) {
		my ($r_id, $r_eml) = (split(/<>/))[0,2];
		# ID�̏d���`�F�b�N
		if($r_id eq $id) {
			$flg |= ID_EXISTS;
		}
		# ���[���A�h���X�̏d���`�F�b�N(�Ǘ��҂ɂ��o�^�̏ꍇ�`�F�b�N���Ȃ�)
		if($notadmin_regist == 1 && $r_eml eq $eml) {
			$flg |= DUPLICATE_EMAIL_ADDRESS;
		}
		# �S�ẴG���[�t���O�������Ă��鎞�ɂ̓��[�v�E�o
		if($flg == (ID_EXISTS | DUPLICATE_EMAIL_ADDRESS) || $notadmin_regist != 1 && $flg == ID_EXISTS) {
			last;
		}
		push(@data, $_);
	}
	if($flg == SUCCESS) {
		# �d�������������ꍇ�ɏ������� 
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
	}
	close(DAT);
	if($flg != SUCCESS) { return $flg; };

	# �p�X���s
	if($pw eq "") {
		my @char = (0 .. 9, 'a' .. 'z', 'A' .. 'Z');
		srand;
		foreach (1 .. 8) {
			$pw .= $char[int(rand(@char))];
		}
	}

	# �Í���
	my $crypt = &encrypt($pw);

	# �p�X���[�h�t�@�C���X�V
	open(DAT,"+< $cf{pwdfile}") or return ID_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	seek(DAT, 0, 2);
	print DAT "$id:$crypt\n";
	close(DAT);

	# �V�K���[�U�[�o�^ ���O�L�^
	if($notadmin_regist == 1) {
		my @tmp = ("$host<>$time<>\n");
		open(REGISTLOG,"+< $cf{regist_log}") or return REGIST_LOG_FILE_OPEN_ERROR;
		while (<REGISTLOG>) {
			my $r_time = (split(/<>/))[1];
			if ($r_time < $repeatitive_regist_boundary_time) {
				last;
			}
			push(@tmp, $_);
		}
		seek(REGISTLOG, 0, 0);
		print REGISTLOG @tmp;
		truncate(REGISTLOG, tell(REGISTLOG));
		close(REGISTLOG);
	}

	return (SUCCESS, $pw, $date);
}

# ���[�U�[���擾
sub read {
	my ($id) = @_;

	# ����t�@�C��
	my (@log, $flg);
	open(IN,"$cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
	while (<IN>) {
		my ($r_id,$nam,$eml,$memo) = split(/<>/);

		if ($r_id eq $id) {
			@log = ($id,$nam,$eml,$memo);
			$flg = 1;
			last;
		}
	}
	close(IN);
	
	if($flg) {
		return (SUCCESS, @log);
	} else {
		return ID_NOTFOUND;
	}
}

# �������[�U�[���擾
sub multiread {
	my ($page, $descending) = @_;
	my @results;

	my $i = 0;
	if($descending == 0) {
		# ���[�U�[�o�^���Â���
		my $fh = File::ReadBackwards->new("$cf{memfile}", "\n") or return MEMBER_FILE_OPEN_ERROR;
		until($fh->eof()) {
			my $line = $fh->readline();
			$i++;
			next if ($i < $page + 1);
			next if ($i > $page + $cf{pg_max});
	
			my @result = split(/<>/, $line);
			push(@results, \@result);
		}
		$fh->close();
	} else {
		# ���[�U�[�o�^���V������
		open(IN,"$cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
		while (<IN>) {
			$i++;
			next if ($i < $page + 1);
			next if ($i > $page + $cf{pg_max});
	
			my @result = split(/<>/);
			push(@results, \@result);
		}
		close(IN);
	}

	return (SUCCESS, $i, @results);
}

# �p�X���[�h�ύX
sub update_password {
	my ($id, $pw, $new_pw, $force) = @_;
	my ($host,$addr) = &get_host;

	# ���[�U�[�o�^�����z�X�g�`�F�b�N
	if($force != 1 && self->$isDenyHost($host,$addr)) { return IS_DENY_HOST; }

	# �Í���
	my $pwd = &encrypt($new_pw);

	# ID�`�F�b�N
	my ($flg, $crypt, @data);
	open(DAT,"+< $cf{pwdfile}") or return ID_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	while (<DAT>) {
		my ($r_id,$r_pw) = split(/:/);

		if ($r_id eq $id) {
			$flg++;
			$crypt = $r_pw;
			$_ = "$id:$pwd\n";
		}
		push(@data,$_);
	}

	if (!$flg) {
		close(DAT);
		return ID_NOTFOUND;
	}

	# �ƍ�
	if($force != 1) {
		chomp($crypt);
		if ( &decrypt($pw, $crypt) != 1 ) {
			close(DAT);
			return (PASS_MISMATCH, $crypt);
		}
	}

	# �p�X�t�@�C���X�V
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	return SUCCESS;
}

# ���[�U�[���ύX
sub update_userinfo {
	my ($id, $name, $email, $memo) = @_;

	# ����t�@�C��
	my @data;
	open(DAT,"+< $cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	while (<DAT>) {
		my ($r_id) = split(/<>/);

		if ($r_id eq $id) {
			$_ = "$r_id<>$name<>$email<>$memo<>\n";
		}
		push(@data,$_);
	}
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	return SUCCESS;
}

sub delete {
	my ($id, $pw, $force) = @_;

	# ID�`�F�b�N
	my ($flg, $crypt, @data);
	open(DAT,"+< $cf{pwdfile}") or return ID_FILE_OPEN_ERROR;
	eval "flock(DAT, 2);";
	while (<DAT>) {
		my ($r_id,$r_pw) = split(/:/);

		if ($r_id eq $id) {
			$flg++;
			$crypt = $r_pw;
			next;
		}
		push(@data,$_);
	}
	if (!$flg) {
		close(DAT);
		return ID_NOTFOUND;
	}

	# �ƍ�
	if($force != 1) {
		chomp($crypt);
		if (&decrypt($pw, $crypt) != 1) {
			close(DAT);
			return PASS_MISMATCH;
		}
	}

	# �p�X�t�@�C���X�V
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	# ����t�@�C��
	my @data;
	open(DAT,"+< $cf{memfile}") or return MEMBER_FILE_OPEN_ERROR;
	while (<DAT>) {
		my ($r_id) = split(/<>/);
		next if ($r_id eq $id);

		push(@data,$_);
	}
	seek(DAT, 0, 0);
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	return SUCCESS;
}

1;
