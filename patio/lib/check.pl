#��������������������������������������������������������������������
#�� [ WebPatio ]
#�� check.pl - 2006/10/08
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

#-------------------------------------------------
#  �`�F�b�N���[�h
#-------------------------------------------------
sub check {
	&header();
	print <<EOM;
<h3>�`�F�b�N���[�h</h3>
<ul>
EOM

	local(%dir) = (
		$logdir, "���O�f�B���N�g��",
		$sesdir, "�Z�b�V�����f�B���N�g��",
		$upldir, "�A�b�v���[�h�f�B���N�g��",
		$thumbdir, "�T���l�C���摜�f�B���N�g��"
	);
	foreach ( keys(%dir) ) {
		if (-d $_) {
			print "<li>$dir{$_}�̃p�X : OK!\n";

			if (-w $_ && -r $_ && -x $_) {
				print "<li>$dir{$_}�̃p�[�~�b�V���� : OK!\n";
			} else {
				print "<li>$dir{$_}�̃p�[�~�b�V���� : NG �� $_\n";
			}
		} else {
			print "<li>$dir{$_}�̃p�X : NG �� $_\n";
		}
	}

	local(%log) = (
		$nowfile,  "���s�t�@�C��",
		$pastfile, "�ߋ��t�@�C��",
		$memfile,  "����t�@�C��",
	);
	foreach ( keys(%log) ) {
		if (-f $_) {
			print "<li>$log{$_}�̃p�X : OK!\n";

			if (-w $_ && -r $_) {
				print "<li>$log{$_}�̃p�[�~�b�V���� : OK!\n";
			} else {
				print "<li>$log{$_}�̃p�[�~�b�V���� : NG �� $_\n";
			}
		} else {
			print "<li>$log{$_}�̃p�X : NG �� $_\n";
		}
	}

	print <<EOM;
<li>�o�[�W���� : $ver
</ul>
</body>
</html>
EOM
	exit;
}


1;

