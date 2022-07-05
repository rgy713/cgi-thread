# ���W���[���錾
use strict;
use Crypt::CBC;
use Crypt::Blowfish;
use File::Basename;
use File::Spec;
use Symbol qw();

use lib qw(./lib);
use Crypt::SaltedHash;
use File::chdir;

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

# ���̃t�@�C�����猩��WebPatio�t�H���_�p�X
$cf{webpatio_path} = '../';

# �Ǘ��p�p�X���[�h
$cf{password} = '0123';

# ���[�U�[�p�X���[�h�Í����L�[
# �ݒu�ꏊ���قȂ�ꍇ�͂��̕������ύX���ĉ�����
my $user_password_encrypt_key = 'f45hcmfTdUh0TUwX';

# �p�X���[�h���s�`��
# 1 : ���[�U����̔��s�������e���\�ɂ���
# 2 : ���s�͊Ǘ��҂̂݁B���[�U�̓����e�̂�
# 3 : ���s�������e�͊Ǘ��҂̂݁iindex.html�͕s�v�j
$cf{pwd_regist} = 1;

# �p�X���[�h�t�@�C���y�T�[�o�p�X�z
$cf{pwdfile} = './data/.htpasswd';

# �A�N�Z�X�����t�@�C���y�T�[�o�p�X�z
$cf{logfile} = './data/.axslog';

# ����t�@�C���y�T�[�o�p�X�z
$cf{memfile} = './data/.member';

# ����ID���s���O�t�@�C���y�T�[�o�p�X�z
$cf{regist_log} = './data/regist.log';

# �e���v���[�g�f�B���N�g���y�T�[�o�p�X�z
$cf{tmpldir} = "./tmpl";

# �����v���O����URL�yURL�p�X�z
$cf{enter_cgi} = './index.cgi';

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
$cf{gethostbyaddr} = 1;

#=====================================================================
#  ���ݒ芮��
#=====================================================================

# �T�[�o�p�X�ݒ�l���΃p�X�ɕϊ�
foreach my $key ('pwdfile', 'logfile', 'memfile', 'regist_log', 'tmpldir') {
	$cf{$key} = File::Spec->rel2abs($cf{$key}, dirname(__FILE__));
}

# WebPatio���瓮��ɕK�v�Ȑݒ�l���擾
{
	# WebPatio init.cgi�ɂ��O���[�o��������h�����߁A
	# �p�b�P�[�W���ꎞ�쐬���Ă���require���Ċu��
	package WebPatioConf;
	use File::Basename;
	use File::Spec;
	require File::Spec->catfile(File::Spec->abs2rel(File::Spec->canonpath(dirname(__FILE__) . '/' . $cf{webpatio_path})), 'init.cgi');

	# �������ݗ������O�t�@�C�������ۑ��֘A�p�X��
	# ���̃t�@�C�����猩�����΃p�X�ƂȂ�悤�ϊ�
	foreach my $key ('history_logdir', 'history_logdir_number', 'history_logfile_count') {
		$WebPatioConf::history_shared_conf{$key} =
			File::Spec->abs2rel(File::Spec->rel2abs($WebPatioConf::history_shared_conf{$key}, $cf{webpatio_path}));
	}

	# �߂��URL�����Ύw��̏ꍇ�A���̃t�@�C�����猩������URL�ƂȂ�悤�ϊ�
	if ($WebPatioConf::history_shared_conf{back_url} !~ /^(?:[a-z]*:\/\/|\/)/i) {
		local $File::chdir::CWD = dirname(__FILE__);
		$WebPatioConf::history_shared_conf{back_url} =
			File::Spec->abs2rel(Cwd::realpath(File::Spec->rel2abs($WebPatioConf::history_shared_conf{back_url}, $cf{webpatio_path})));
	}

	# WebPatio Cookie�̃L�[���̈ꕔ�Ɏg�p����f�B���N�g���p�X�̎擾
	$cf{webpatio_cookie_current_dirpath} = do {
		my $dir_separator_regex = quotemeta(File::Spec->canonpath('/'));
		# �h�L�������g���[�g�x�[�X��CGI���s�p�X���擾���A�p�X���N���[���ɂ���
		my $tmp_dirpath = dirname(dirname(dirname($ENV{'SCRIPT_NAME'}) . '/' . $cf{webpatio_path}));
		$tmp_dirpath =~ s/(^${dir_separator_regex}?|${dir_separator_regex}?$)//g;
		# URL�G���R�[�h
		$tmp_dirpath =~ s/(\W)/'%' . unpack('H2', $1)/eg;
		$tmp_dirpath =~ s/\s/+/g;
		$tmp_dirpath;
	};

	# �ݒ�l�擾
	%cf = (%cf, %WebPatioConf::history_shared_conf);

	# WebPatioConf�p�b�P�[�W���폜
	Symbol::delete_package('WebPatioConf');

	# WebPatio ���C�u�����p�X����
	$cf{webpatio_lib_path} = File::Spec->catfile($cf{webpatio_path}, 'lib');
}

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
#  �������
#-----------------------------------------------------------
sub message {
	my ($ttl, $msg, $back_msg, $back_url) = @_;

	# �߂�{�^�����b�Z�[�W
	if (!defined($back_msg) || $back_msg eq '') {
		$back_msg = 'TOP�ɖ߂�';
	}

	# �߂��URL
	if (!defined($back_url) || $back_url eq '') {
		$back_url = "location.href='$cf{back_url}'";
	} else {
		$back_url = "location.href='$back_url'";
	}

	# �e���v���[�g�ǂݍ���
	open(IN,"$cf{tmpldir}/message.html") or &error("open err: message.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �u������
	$tmpl =~ s/!page_ttl!/$ttl/g;
	$tmpl =~ s/!message!/$msg/g;
	$tmpl =~ s/!back_msg!/$back_msg/g;
	$tmpl =~ s/!back_url!/$back_url/g;

	# �\��
	print "Content-type: text/html\n\n";
	&footer($tmpl);
}

#-----------------------------------------------------------
#  crypt�Í�
#-----------------------------------------------------------
sub encrypt {
	my ($plaintext) = @_;

	my $cipher = Crypt::CBC->new(
		{
			key    => $user_password_encrypt_key,
			cipher => 'Blowfish'
		}
	);

	return $cipher->encrypt_hex($plaintext);
}

#-----------------------------------------------------------
#  crypt����
#-----------------------------------------------------------
sub decrypt {
	my ($ciphertext) = @_;

	my $cipher = Crypt::CBC->new(
		{
			key    => $user_password_encrypt_key,
			cipher => 'Blowfish'
		}
	);

	return $cipher->decrypt_hex($ciphertext);
}

#-----------------------------------------------------------
#  �n�b�V����
#-----------------------------------------------------------
sub saltedhash_encrypt {
	my ($plaintext) = @_;

	my $cipher = Crypt::SaltedHash->new(
		algorithm => 'SHA-1'
	);

	$cipher->add($plaintext);
	return $cipher->generate();
}

#-----------------------------------------------------------
#  �n�b�V���ƍ�
#-----------------------------------------------------------
sub saltedhash_verify {
	my ($ciphertext, $verify_target) = @_;

	return Crypt::SaltedHash->validate($ciphertext, $verify_target);
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

