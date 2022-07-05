package cgiprot;
#��������������������������������������������������������������������
#��  WebProtect�pCGI�������W���[�� v4.0
#��  cgiprot.cgi - 2011/05/29
#��  Copyright (c) KentWeb
#��  http://www.kent-web.com/
#��������������������������������������������������������������������
# �y���ӎ����z
#
# 1. ���̃��W���[���� WebProtect (protect.cgi) ��CGI���A�N�Z�X��������
#    ���߂̂��̂ł��B
# 2. ���̃��W���[���́Aprotect.cgi�y�уA�N�Z�X��������CGI�X�N���v�g��
#    �u�K���v�����f�B���N�g�����ɒu���ĉ������B
# 3. �A�X�L�[���[�h��FTP�]�����A�p�[�~�b�V������644�ɐݒ肵�܂��B
# 4. �A�N�Z�X����������CGI�X�N���v�g�ŁA
#    require './jcode.pl';
#    �̉��t�߂Ɉȉ���2�s�����������܂��B
#    ---------------------
#    require './cgiprot.cgi';
#    &cgiprot::check;
#    ---------------------
# 5. ���̃��W���[�����g�p���������Ȃ�s���v�E���Q���Ɋւ��āA��҂�
#    ���̐ӂ͈�ؕ����܂���B

#===========================================================
# ���ݒ荀�� : Web Protect��init.cgi�Ɠ����ɂ��邱��
#===========================================================

# �A�N�Z�X�����t�@�C��
$cf{logfile} = './data/.axslog';

# �F�،�̗L�����ԁi���j
# �� �������O�C�����Ă���̗L������
$cf{job_time} = 60;

# �z�X�g�擾���@
# 0 : gethostbyaddr�֐����g��Ȃ�
# 1 : gethostbyaddr�֐����g��
$cf{gethostbyaddr} = 0;

#===========================================================
# ���ݒ芮��
#===========================================================

#-----------------------------------------------------------
#  �`�F�b�N����
#-----------------------------------------------------------
sub check {
	# ���Ԏ擾
	$ENV{TZ} = "JST-9";
	my $now = time;

	# �z�X�g���擾
	my $host = &get_host;

	# ���O
	my ($flg,$time);
	open(IN,"$cf{logfile}") || &error("Open Err: $cf{logfile}");
	while (<IN>) {
		my ($id,$date,$hos,$ag,$tim) = split(/<>/);

		if ($host eq $hos) {
			$flg++;
			$time = $tim;
			last;
		}
	}
	close(IN);

	# �z�X�g���Ȃ�
	if (!$flg) {
		&error("Host not found");
	# ���Ԑ؂�
	} elsif ($now - $time > $cf{job_time}*60) {
		&error("Time is Over!");
	}
}

#-----------------------------------------------------------
#  �G���[����
#-----------------------------------------------------------
sub error {
	my $err = shift;

	print <<EOM;
Content-type: text/html

<html>
<body>$err</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �z�X�g���擾
#-----------------------------------------------------------
sub get_host {
	my $host = $ENV{'REMOTE_HOST'};
	my $addr = $ENV{'REMOTE_ADDR'};

	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}
	if ($host eq "") { $host = $addr; }

	return $host;
}


1;

