# ���W���[���錾
use strict;
my %cf;
#��������������������������������������������������������������������
#�� WEB PROTECT : init.cgi - 2013/04/06
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������
$cf{version} = 'Web Protect v4.33';
#��������������������������������������������������������������������
#�� [���ӎ���]
#�� 1. ���̃X�N���v�g�̓t���[�\�t�g�ł��B���̃X�N���v�g���g�p����
#��    �����Ȃ鑹�Q�ɑ΂��č�҂͈�؂̐ӔC�𕉂��܂���B
#�� 2. �ݒu�Ɋւ��鎿��̓T�|�[�g�f���ɂ��肢�������܂��B
#��    ���ڃ��[���ɂ�鎿��͈�؂��󂯂������Ă���܂���B
#��������������������������������������������������������������������

#=====================================================================
#  ���ݒ荀��
#=====================================================================

# �Ǘ��p�p�X���[�h
$cf{password} = 'pass';

# �p�X���[�h���s�`��
# 1 : ���[�U����̔��s�������e���\�ɂ���
# 2 : ���s�͊Ǘ��҂̂݁B���[�U�̓����e�̂�
# 3 : ���s�������e�͊Ǘ��҂̂݁iindex.html�͕s�v�j
$cf{pwd_regist} = 1;

# �Ǘ��҃��[���A�h���X
# �� $cf{pwd_regist} = 1; �̂Ƃ�
$cf{master} = 'xxx@xxx.xx';

# sendmail�p�X�y�T�[�o�p�X�z
# �� $cf{pwd_regist} = 1; �̂Ƃ�
$cf{sendmail} = '/usr/lib/sendmail';

# sendmail�� -f�I�v�V����
# �� �T�[�o�d�l�ŕK�v�ȏꍇ
$cf{sendm_f} = 0;

# �F�،�̗L�����ԁi���j
# �� �������O�C�����Ă���̗L������
$cf{job_time} = 60;

# �B���t�@�C���i�g�b�v�j
# �� ""�̒��Ƀt�@�C�����݂̂��L�q
${$cf{secret}}[0] = "top.html";

# �ȉ��͉B���t�@�C���i���y�[�W�ȍ~���j
# �� [1][2][3]... �Ƒ�����B""�̒��Ƀt�@�C�����݂̂��L�q�B
# �� CGI�̏ꍇ��http://����L�q����B
${$cf{secret}}[1] = "file1.html";
${$cf{secret}}[2] = "file2.html";
${$cf{secret}}[3] = "file3.html";

# �o�C�i���t�@�C��
# �� �L�[�i�����j�̓p�����[�^
# �� �l�i�E���j�͏��ɁA�u�w�b�_�[�v�u�g���q�v���R���}�ŋ�؂�
$cf{binary} = {
		gif   => "image/gif,gif",
		jpeg  => "image/jpeg,jpg",
		pdf   => "aplication/pdf,pdf",
		excel => "application/ms-excel,xls",
	};

# �B���f�B���N�g���y�T�[�o�p�X�z
# �� �O�����璼�ڃA�N�Z�X�ł��Ȃ��ꏊ�̂ق����悢
$cf{prvdir} = './private';

# �Z�b�V�����f�B���N�g���y�T�[�o�p�X�z
$cf{sesdir} = "./ses";

# �p�X���[�h�t�@�C���y�T�[�o�p�X�z
$cf{pwdfile} = './data/.htpasswd';

# �A�N�Z�X�����t�@�C���y�T�[�o�p�X�z
$cf{logfile} = './data/.axslog';

# ����t�@�C���y�T�[�o�p�X�z
$cf{memfile} = './data/.member';

# �e���v���[�g�f�B���N�g���y�T�[�o�p�X�z
$cf{tmpldir} = "./tmpl";

# �{�̃v���O����URL�yURL�p�X�z
$cf{protect_cgi} = './protect.cgi';

# �����v���O����URL�yURL�p�X�z
$cf{enter_cgi} = './enter.cgi';

# �o�^�v���O����URL�yURL�p�X�z
$cf{manager_cgi} = './manager.cgi';

# �Ǘ��v���O����URL�yURL�p�X�z
$cf{admin_cgi} = './admin.cgi';

# �ő�󗝃T�C�Y
# �� �v���O�����Ƃ��Ď󗝉\�ȃT�C�Y
# �� Byte�Ŏw�肷�� [��] 1024 = 1KB
$cf{maxdata} = 10240;

# �A�N�Z�X���O�ő�ێ���
$cf{max_log} = 300;

# �P�y�[�W�������\�������i�Ǘ���ʁj
$cf{pg_max} = 10;

# ���[�U�o�^�A�N�Z�X�����i���p�X�y�[�X�ŋ�؂�j
#  �� ���ۂ���z�X�g������IP�A�h���X���L�q�i�A�X�^���X�N�j
#  �� �L�q�� $deny = '*.anonymizer.com 211.154.120.*';
$cf{deny} = '';

# �z�X�g�擾���@
# 0 : gethostbyaddr�֐����g��Ȃ�
# 1 : gethostbyaddr�֐����g��
$cf{gethostbyaddr} = 0;

# �p�X���[�h���s�`�Ԃ����[�U����ɂ����ꍇ�̊�����ʂ̖߂��yURL�p�X�z
$cf{back_url} = "../index.html";

# �V�K���[�U�[�o�^�Ԋu�i�b�j
$cf{wait_regist} = 60;

# �V�K���[�U�[�o�^���O�t�@�C��
$cf{regist_log} = './data/regist.log';

# �V�K���[�U�[�o�^�����[���A�h���X�֎~���[�h(���Ԉ�v)
# ���[���A�h���X�Ɋ܂ނ��Ƃ��֎~���镶������J���}��؂�Ŏw�肵�܂�
# (�啶������������ʂ����ɋ֎~���[�h�̔�����s���܂�)
$cf{deny_email} = '';

#=====================================================================
#  ���ݒ芮��
#=====================================================================

# �ݒ�l��Ԃ�
sub init {
	return %cf;
}

#-----------------------------------------------------------
#  �t�H�[���f�R�[�h
#-----------------------------------------------------------
sub parse_form {
	my ($buf,%in);
	if ($ENV{REQUEST_METHOD} eq "POST") {
		&error('�󗝂ł��܂���') if ($ENV{CONTENT_LENGTH} > $cf{maxdata});
		read(STDIN, $buf, $ENV{CONTENT_LENGTH});
	} else {
		$buf = $ENV{QUERY_STRING};
	}
	foreach ( split(/&/, $buf) ) {
		my ($key,$val) = split(/=/);
		$key =~ tr/+/ /;
		$key =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;
		$val =~ tr/+/ /;
		$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

		# ������
		$val =~ s/&/&amp;/g;
		$val =~ s/</&lt;/g;
		$val =~ s/>/&gt;/g;
		$val =~ s/"/&quot;/g;
		$val =~ s/'/&#39;/g;
		$val =~ s/[\r\n]//g;

		$in{$key} .= "\0" if (defined($in{$key}));
		$in{$key} .= $val;
	}
	return %in;
}

#-----------------------------------------------------------
#  �G���[���
#-----------------------------------------------------------
sub error {
	my $err = shift;

	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!error!/$err/g;

	print "Content-type: text/html\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  crypt�Í�
#-----------------------------------------------------------
sub encrypt {
	my ($in) = @_;

	my @wd = ('a'..'z', 'A'..'Z', '0'..'9', '.', '/');
	srand;
	my $salt = $wd[int(rand(@wd))] . $wd[int(rand(@wd))];
	crypt($in, $salt) || crypt ($in, '$1$' . $salt);
}

#-----------------------------------------------------------
#  crypt�ƍ�
#-----------------------------------------------------------
sub decrypt {
	my ($in, $dec) = @_;

	my $salt = $dec =~ /^\$1\$(.*)\$/ ? $1 : substr($dec, 0, 2);
	if (crypt($in, $salt) eq $dec || crypt($in, '$1$' . $salt) eq $dec) {
		return 1;
	} else {
		return 0;
	}
}

#-----------------------------------------------------------
#  ���Ԏ擾
#-----------------------------------------------------------
sub get_time {
	# �^�C���]�[���ݒ�
	$ENV{TZ} = "JST-9";

	# ���Ԏ擾
	my $time = time;
	my ($sec,$min,$hour,$mday,$mon,$year) = (localtime($time))[0..5];

	# �t�H�[�}�b�g
	my $date = sprintf("%04d/%02d/%02d-%02d:%02d:%02d",
				$year+1900,$mon+1,$mday,$hour,$min,$sec);

	return ($time,$date);
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

	return ($host,$addr);
}

#-----------------------------------------------------------
#  �t�b�^�[
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# ���쌠�\�L�i�폜�E���ϋ֎~�j
	my $copy = <<EOM;
<p align="center" style="margin-top:3em;font-size:10px;font-family:verdana,helvetica,arial,osaka;">
- <a href="http://www.kent-web.com/" target="_top">WebProtect</a> -
</p>
EOM

	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}


1;

