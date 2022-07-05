#��������������������������������������������������������������������
#�� [ WebPatio ]
#�� edit_log.pl - 2007/06/06
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# 2009/12/07 ���O�̕ҏW���ʂ����[�����郋�[�`���� $mailing �̃I�v�V������K�p����悤��
# 2009/07/06 ���O���폜�����Ƃ��ɃJ�E���g���������W�b�N�ύX
#            ���O�����[�U�[���ҏW�����Ƃ��A���̃^�C���X�^���v���X���b�h�ꗗ�̃^�C���X�^���v�ɂ���悤�ɕύX
# 2009/06/26 ���O��ҏW����ہA�ʃ��O��$key�ŏ㏑������index���X�V����̂ɁA�ϐ��Ɋi�[���Ă����̂Ŏ̂Ă�悤�ɂ���
#            ���O�ҏW��A�Ǘ����[�h�̑��s�ƁA�Ǘ����[�h�̏I�����I�ׂ�悤�ɂ���
# 2009/06/15 ���O��ҏW����ہA���X�����J�E���g���������W�b�N���ԈႦ�Ă����̂ŏC��
# 2009/05/29 ���[�U�[�ԃ��[�����M�𗘗p���Ȃ��ݒ�̂Ƃ��ɃA�C�R�����\����
# 2007/01/09 �Ǘ��҃��b�N���A�Ǘ��҂͕ҏW�ł���悤�ɒ���
# 2007/12/17 �Ǘ��҂ɂ��ҏW���ɁA�p�X���[�h���������ǂ����I�v�V�����Ŏw��ł���悤�ɂ����B
# 2007/09/30 �L���ҏW���A���[���A�h���X���͂̐�������Ă���̂ɑΉ����Ă��Ȃ������_���C��
# 2007/06/13 �Ǘ��҂ɂ��ҏW���ɂ́A�������݂̃p�X���[�h�������悤�ɁB�ҏW���e�����ɖ߂����[�U�[���������߁B
# 2007/06/10 3.2�����ɏC��
# 2007/05/01 �e�L�����C������Ɩ��O��������o�O�C��
# 2007/05/01 3.13�ɑΉ�
#            ���O���G�f�B�^�[�Œ��ڕҏW���邱�Ƃ�z�肵�āA�L���ҏW���ɂ́A���X�̐����J�E���g�������悤��
# ���肵�܂ɂ������� 2007.04.06

use List::Util qw/max/;

#-------------------------------------------------
#  �L���C��
#-------------------------------------------------
sub edit_log {
	local $j;
	local($myjob) = @_;

	if ($myjob eq "admin") {
		$in{'f'}  = $in{'no'};
		$in{'no'} = $in{'no2'};
	}
	local($mylog,$idxfile);
	if ($in{'bakfile'}) {
		$idxfile = $pastfile;
		$mylog = 'bakfile';
	} else {
		$idxfile = $nowfile;
		$mylog = 'logfile';
	}

	# �����`�F�b�N
	$in{'f'}  =~ s/\D//g;
	$in{'no'} =~ s/\D//g;

	# �X���b�h���O�t�@�C���p�X�擾
	my $logfile_path = get_logfolder_path($in{'f'}) . "/$in{'f'}.cgi";

	# �Y�t�t�@�C���ő吔
	my $max_upl_num = 3 + $upl_increase_num;

	# �C������
	if ($in{'job'} eq "edit2") {

		# �Ǘ��҃I�y
		if ($in{'pass'} ne "") {
			$admin_flag = 1;
			if ($in{'pass'} ne $pass) { &error("�p�X���[�h���Ⴂ�܂�"); }
		# ���[�U�[��ʂ���Ǘ��p�X�����
		} elsif ($in{'pwd'} eq $pass) {
			$admin_flag = 1;

		# ���[�U�I�y
		} elsif ($in{'pwd'} ne "") {
			$admin_flag = 0;

			# �`�F�b�N
			if ($no_wd) { &no_wd; }
			if ($jp_wd) { &jp_wd; }
			if ($urlnum > 0) { &urlnum; }

		# �I�y�s��
		} else {
			&error("�s���ȃA�N�Z�X�ł�");
		}

		# ���e���e�`�F�b�N
		if ($i_com eq "") { &error("�R�����g�̓��e������܂���"); }
		if ($i_nam eq "") {
			if ($in_name) { &error("���O�͋L���K�{�ł�"); }
			else { $i_nam = '������'; }
		}
#		if ($in_mail && $in{'email'} eq "") { &error("E-mail�͋L���K�{�ł�"); }
	if ($in_mail == 1 && $in{'email'} eq "") { &error("E-mail�͋L���K�{�ł�"); }
	if ($in_mail == 2 && $in{'email'} ne "") { &error("E-mail�͓��͋֎~�ł�"); }
	if ($in_mail == 3 && $in{'email'} ne "") { &error("E-mail�͓��͋֎~�ł�"); }
		if ($in{'email'} && $in{'email'} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,6}$/)
			{ &error("E-mail�̓��͓��e���s���ł�"); }
		if ($i_sub eq "")
			{ &error("�^�C�g���͋L���K�{�ł�"); }
		if ($i_sub =~ /^(\x81\x40|\s)+$/)
			{ &error("�^�C�g���͐������L�����Ă�������"); }
		if ($i_nam =~ /^(\x81\x40|\s)+$/)
			{ &error("���O�͐������L�����Ă�������"); }
		if ($i_com =~ /^(\x81\x40|\s|<br>)+$/)
			{ &error("�R�����g�͐������L�����Ă�������"); }
		if ($in{'url'} eq "http://") { $in{'url'} = ""; }

		local($top, $new_log);
		open(DAT, "+<", $logfile_path) || &error("Open Error: $in{'f'}.cgi");
		eval "flock(DAT, 2);";
		$top = <DAT>;
#		$j = -1;
		# �w�b�_
		my ($num,$sub2,$res,$key) = split(/<>/, $top);
        my $last_log;
        my $res_cnt = 0; # �ŏI���X��񌈒�p���X���J�E���^ (���O�ɋL�^���郌�X����$res�����̂܂܎g�p)
		while(<DAT>) {
			local $idcrypt;
			my ($no,$sub,$nam,$eml,$com,$dat,$hos,$pw,$url,$mvw,$myid,$tim,$upl1,$upl2,$upl3,$user_id,$is_sage,
				$cookie_a,$history_id,$log_useragent,$is_private_browsing_mode,$first_access_datetime,$upl4,$upl5,$upl6);

			$_ =~ s/(?:\r\n|\r|\n)$//;
			($no,$sub,$nam,$eml,$com,$dat,$hos,$pw,$url,$mvw,$myid,$tim,$upl1,$upl2,$upl3,$idcrypt,$user_id,$is_sage,
				$cookie_a,$history_id,$log_useragent,$is_private_browsing_mode,$first_access_datetime,$upl4,$upl5,$upl6) = split(/<>/, $_);

			if ($tim eq "") { &error("���̋L���̓A�b�v���[�h�ł��܂���"); }

			if ($in{'no'} == $no) {
				# �p�X�`�F�b�N
				if (!$admin_flag) {
					if (!&decrypt($in{'pwd'}, $pw)) {
						&error("�p�X���[�h���Ⴂ�܂�");
					}
				}

				# �g���b�v
				unless ($i_nam =~ /��/ && $i_nam eq $nam) {
					$i_nam = &trip($i_nam);
				}

				# �摜�����擾
				my (%fn, %ex, %w, %h, %thumb_w, %thumb_h, %image_orig_md5, %image_conv_md5);
				my @upls = ($upl1, $upl2, $upl3, $upl4, $upl5, $upl6);
				foreach my $i (1 .. 6) {
					($fn{$i}, $ex{$i}, $w{$i}, $h{$i},
						$thumb_w{$i}, $thumb_h{$i}, $image_orig_md5{$i}, $image_conv_md5{$i}) = split(/,/, $upls[$i - 1]);

					# �Y�t�폜
					if ($in{"del$i"} || $image_upl && $i <= $max_upl_num && $in{"upfile$i"}) {
						unlink("$upldir/$fn{$i}/$tim-$i$ex{$i}");
						unlink("$thumbdir/$fn{$i}/$tim-${i}_s.jpg");

						($fn{$i}, $ex{$i}, $w{$i}, $h{$i},
							$thumb_w{$i}, $thumb_h{$i}, $image_orig_md5{$i}, $image_conv_md5{$i}) = ();
					}
				}

				# �Y�t�A�b�v
				if ($image_upl && grep { $in{'upfile' . $_} } (1 .. $max_upl_num)) {
					require $upload;
					my (%tmp_fn, %tmp_ex, %tmp_w, %tmp_h, %tmp_thumb_w, %tmp_thumb_h, %tmp_image_orig_md5, %tmp_image_conv_md5);
					($tmp_fn{1},$tmp_ex{1},$tmp_w{1},$tmp_h{1},$tmp_thumb_w{1},$tmp_thumb_h{1},$tmp_image_orig_md5{1},$tmp_image_conv_md5{1},
						$tmp_fn{2},$tmp_ex{2},$tmp_w{2},$tmp_h{2},$tmp_thumb_w{2},$tmp_thumb_h{2},$tmp_image_orig_md5{2},$tmp_image_conv_md5{2},
						$tmp_fn{3},$tmp_ex{3},$tmp_w{3},$tmp_h{3},$tmp_thumb_w{3},$tmp_thumb_h{3},$tmp_image_orig_md5{3},$tmp_image_conv_md5{3},
						$tmp_fn{4},$tmp_ex{4},$tmp_w{4},$tmp_h{4},$tmp_thumb_w{4},$tmp_thumb_h{4},$tmp_image_orig_md5{4},$tmp_image_conv_md5{4},
						$tmp_fn{5},$tmp_ex{5},$tmp_w{5},$tmp_h{5},$tmp_thumb_w{5},$tmp_thumb_h{5},$tmp_image_orig_md5{5},$tmp_image_conv_md5{5},
						$tmp_fn{6},$tmp_ex{6},$tmp_w{6},$tmp_h{6},$tmp_thumb_w{6},$tmp_thumb_h{6},$tmp_image_orig_md5{6},$tmp_image_conv_md5{6}) = &upload($tim, $in{'increase_num'}, 1);

					foreach my $i (1 .. $max_upl_num) {
						if (!$tmp_ex{$i}) {
							next;
						}
						($fn{$i},$ex{$i},$w{$i},$h{$i},$thumb_w{$i},$thumb_h{$i},$image_orig_md5{$i},$image_conv_md5{$i})
							= ($tmp_fn{$i},$tmp_ex{$i},$tmp_w{$i},$tmp_h{$i},$tmp_thumb_w{$i},$tmp_thumb_h{$i},$tmp_image_orig_md5{$i},$tmp_image_conv_md5{$i});
					}
				}

				# ���X�����X�V
				if ($admin_flag) {
					# �Ǘ��҂̕ҏW�͋L�^�������ێ�����
					$time = $tim;
					$date = $dat;

					# �p�X���[�h�N���A�t���O�������Ă���ꍇ�́A�p�X���[�h���󗓂ɂ���
					if ($in{'clearpass'}) {
						$pw = '';
					}
				} else {
					# �Ǘ��҈ȊO�̕ҏW�͋L�^���������ݓ����ɍX�V
					# ($tim���X�V���Ă��܂��ƁA�Y�t�t�@�C���A�N�Z�X�Ɏx�Ⴊ�o�邽�߂��̂܂܂Ƃ���)
					$dat = $date;

					# �Ǘ��҈ȊO�̕ҏW�ł�ID���쐬���Ȃ���
					if($idkey) { &makeid; }
					else { $idcrypt = "";}
				}

				# �X�V���郍�O�s���쐬
				$_ = join('<>',
					$no,
					$in{'sub'},
					$i_nam,
					$in{'email'},
					$in{'comment'},
					$dat,
					$host,
					$pw,
					$in{'url'},
					$in{'mvw'},
					$myid,
					$tim,
					"$fn{1},$ex{1},$w{1},$h{1},$thumb_w{1},$thumb_h{1},$image_orig_md5{1},$image_conv_md5{1}",
					"$fn{2},$ex{2},$w{2},$h{2},$thumb_w{2},$thumb_h{2},$image_orig_md5{2},$image_conv_md5{2}",
					"$fn{3},$ex{3},$w{3},$h{3},$thumb_w{3},$thumb_h{3},$image_orig_md5{3},$image_conv_md5{3}",
					$idcrypt,
					$user_id,
					$is_sage,
					$cookie_a,
					$history_id,
					$log_useragent,
					$is_private_browsing_mode,
					$first_access_datetime,
					"$fn{4},$ex{4},$w{4},$h{4},$thumb_w{4},$thumb_h{4},$image_orig_md5{4},$image_conv_md5{4}",
					"$fn{5},$ex{5},$w{5},$h{5},$thumb_w{5},$thumb_h{5},$image_orig_md5{5},$image_conv_md5{5}",
					"$fn{6},$ex{6},$w{6},$h{6},$thumb_w{6},$thumb_h{6},$image_orig_md5{6},$image_conv_md5{6}",
					'' # ���s�̂��߂̃_�~�[�v�f
				);
			}
			$new_log .= "$_\n";
			$last_log = $_;
			$res_cnt++;
#			$j++;
		}

		# �e�L���̏ꍇ�͑薼���X�V
		if ($in{'no'} == 1) { $sub2 = $in{'sub'}; }

		seek(DAT, 0, 0);
		print DAT "$num<>$sub2<>$res<>$key<>\n" . $new_log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# �ŏI���e�Җ�
#		($last_nam) = (split(/<>/, $new[$#new]))[2];
		# �Ǝ��ԁE�^�C�g�����擾
		($last_sub,$last_nam,$last_dat) = (split(/<>/, $last_log))[1,2,5];

		$res_cnt--; # ���X�J�E���g����e���X������
		if ($res_cnt == 0) {
			# �ŏI�I�Ƀ��X���Ȃ��ꍇ
#			$last_nam = "";
#			$last_dat = "";
			$last_sub = "";
#			$last_tim = "";
		}

		# index�W�J
		my $data;
		open(DAT,"+< $idxfile") || &error("Open Error: $idxfile");
		eval "flock(DAT, 2);";
		$top = <DAT> if (!$in{'bakfile'});
		while(<DAT>) {
			chomp($_);
#			local($no,$sub,$res,$nam,$da,$na2,$key2,$upl,$ressub,$restime) = split(/<>/);
			local($no,$sub,$re,$nam,$da,$na2,undef,$upl,$ressub,$restime) = split(/<>/);
			chomp ($ressub);
			chomp ($restime);

			if ($in{'f'} == $no) {
				if (!$admin_flag ) {
					$restime=$time;
				}
				# �e�L���C���̂Ƃ�
				if ($in{'no'} == 1) {

					# �e���O
					local($tim,$upl1,$upl2,$upl3,$upl4,$upl5,$upl6) = (split(/<>/, $new[1]))[11 .. 14, 23 .. 25];
					my $ex1 = (split(/,/, $upl1))[1];
					my $ex2 = (split(/,/, $upl2))[1];
					my $ex3 = (split(/,/, $upl3))[1];
					my $ex4 = (split(/,/, $upl4))[1];
					my $ex5 = (split(/,/, $upl5))[1];
					my $ex6 = (split(/,/, $upl6))[1];
					if ($ex1 || $ex2 || $ex3 || $ex4 || $ex5 || $ex6) { $upl = $tim; } else { $upl = ''; }

#					if ($res2 == 0) { $na2 = $i_nam; }
#					if ($j < 1) { $last_sub = ""; }
					$_ = "$no<>$in{'sub'}<>$res<>$i_nam<>$da<>$last_nam<>$key<>$upl<>$last_sub<>$restime<>";

				# ���X�L���C���̂Ƃ�
				} else {
					$_ = "$no<>$sub<>$res<>$nam<>$da<>$last_nam<>$key<>$upl<>$last_sub<>$restime<>";
				}
			}
			$data .= "$_\n";
		}

		# index�X�V
		$data = $top . $data if (!$in{'bakfile'});
		seek(DAT, 0, 0);
		print DAT $data;
		truncate(DAT, tell(DAT));
		close(DAT);

# �ҏW���ʑ��M *�Վ��[�u
if ($mailing!=0) {
	# ���[���^�C�g�����`
	$msub = "$title�F \[$no\] $sub";

	# �{���̉��s�E�^�O�𕜌�
	$mcom = $in{'comment'};
	$mcom =~ s/<br>/\n/g;
	$mcom =~ s/&lt;/��/g;
	$mcom =~ s/&gt;/��/g;
	$mcom =~ s/&quot;/�h/g;
	$mcom =~ s/&amp;/��/g;

$mbody = <<EOM;
--------------------------------------------------------
$title�̋L�����ҏW����܂����B

���e�����F$dat
�z�X�g���F$host
�u���E�U�F$ENV{'HTTP_USER_AGENT'}

���Ȃ܂��F$i_nam2
�d���[���F$in{'email'}
�^�C�g���F$in{'sub'}
�t�q�k  �F$in{'url'}

$mcom
--------------------------------------------------------
EOM

	# �薼��BASE64��
	$msub = &base64($msub);

	# ���[���A�h���X���Ȃ��ꍇ�͊Ǘ��҃A�h���X�ɒu������
	if ($in{'email'} eq "") { $email = $mailto; }
	else { $email = $in{'email'}; }

	# sendmail���M
	open(MAIL,"| $sendmail -t -i") || &error("���M���s");
	print MAIL "To: $mailto\n";
	print MAIL "From: $email\n";
	print MAIL "Subject: $msub\n";
	print MAIL "MIME-Version: 1.0\n";
	print MAIL "Content-type: text/plain; charset=ISO-2022-JP\n";
	print MAIL "Content-Transfer-Encoding: 7bit\n";
	print MAIL "X-Mailer: $ver\n\n";
	foreach ( split(/\n/, $mbody) ) {
		&jcode'convert(*_, 'jis', 'sjis');
		print MAIL $_, "\n";
	}
	close(MAIL);
}

		# �������b�Z�[�W
		&header;
		print "<blockquote>\n";
		print "<b>�C�����������܂���</b><br>\n";

		# �Ǘ����[�h
		if ($myjob eq "admin" || $in{'myjob'} eq "admin") {
		print "�Ǘ����[�h���s\n";
		print "<table><tr><td valign=top>\n";
			print "<form action=\"$admincgi\" method=\"post\">\n";
			print "<input type=\"hidden\" name=\"pass\" value=\"$in{'pass'}\">\n";
			print "<input type=\"hidden\" name=\"mode\" value=\"admin\">\n";
			print "<input type=\"hidden\" name=\"$mylog\" value=\"1\">\n";
			print "<input type=\"submit\" value=\"�X���b�h�ꗗ�֖߂�\"></form>\n";

		print "</td><td width=15></td>\n";
		print "<td valign=top>\n";

			print "<form action=\"$admincgi\" method=\"post\">\n";
			print "<input type=\"hidden\" name=\"pass\" value=\"$in{'pass'}\">\n";
			print "<input type=\"hidden\" name=\"mode\" value=\"admin\">\n";
			print "<input type=\"hidden\" name=\"$mylog\" value=\"1\">\n";
			print "<input type=\"hidden\" name=\"action\" value=\"view\">\n";
			print "<input type=\"hidden\" name=\"no\" value=\"$in{'f'}\">\n";
			print "<input type=\"submit\" value=\"�ʃ����e�֖߂�\"></form>\n";
		print "</td></tr></table>\n";

		print "�Ǘ����[�h�I��\n";

		}
		# ��ʃ��[�h
#		} else {

		print "<table><tr><td valign=top>\n";

			print "<form action=\"$bbscgi\">\n";
			print "<input type=\"submit\" value=\"�f���֖߂�\"></form>\n";
#		}

		# �X���b�h�ɖ߂�
		print "</td><td width=15></td>\n";
		print "<td valign=top>\n";
		# ��ʃ��[�h
#		} else {
			print "<form action=\"$readcgi\">\n";
			print "<input type=\"hidden\" name=\"no\" value=\"$in{'f'}\">\n";
			print "<input type=\"submit\" value=\"�X���b�h�֖߂�\"></form>\n";
#		}

		print "</td></tr></table>\n";

		print "</blockquote></body></html>\n";
		exit;
	}

	# �Y�����O�`�F�b�N
	local($flg, $top);
	open(IN, $logfile_path);
	$top = <IN>;
	while (<IN>) {
		$_ =~ s/(?:\r\n|\r|\n)$//;
		($no,$sub,$nam,$eml,$com,$dat,$hos,$pw,$url,$mvw,$myid,$tim,$upl{1},$upl{2},$upl{3},$user_id,$is_sage,$cookie_a,$history_id,
			$upl{4},$upl{5},$upl{6}) = (split(/<>/))[0 .. 14, 16 .. 19, 23 .. 25];

		last if ($in{'no'} == $no);
	}
	close(IN);

	# �Ǘ��҃��b�N���̓��[�U�[�͕ҏW�s��
	local(undef,undef,undef,$key) = split(/<>/, $top);
	if ($in{'pass'} ne $pass && $in{'pwd'} ne $pass && $key == 4) {
			&error("�Ǘ��҃��b�N����Ă���L���͕ҏW�ł��܂���");
	}
	if ($myjob eq "user" && $in{'pwd'} ne $pass) {
		if ($pw eq "") {
			if ($clearpass == 1) {
			&error("�Y���L���̓p�X���[�h���ݒ肳��Ă��܂���B�܂��A�Ǘ��҂ɂ��ҏW���ꂽ�ꍇ���ҏW�ł��Ȃ��Ȃ�ݒ�ɂȂ��Ă��܂��B");
			} else {
			&error("�Y���L���̓p�X���[�h���ݒ肳��Ă��܂���");
			}
		}
		if (!&decrypt($in{'pwd'}, $pw)) { &error("�p�X���[�h���Ⴂ�܂�"); }
	}
#	  elsif ($in{'pwd'} eq $pass) {
#		$myjob eq "admin";
#	}

	if ($smile) { &header("", "js"); }
	else { &header(); }

	print <<"EOM";
<div align="center">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr bgcolor="$col1"><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col3"><td bgcolor="$col3" nowrap width="92%">
<img src="$imgurl/mente.gif" align="top">
&nbsp; <b>�L���C���t�H�[��</b></td>
<td align="right" bgcolor="$col3" nowrap>
<a href="javascript:history.back()">�O��ʂɖ߂�</a></td>
</tr></table></Td></Tr></Table>
<p>
EOM

	if ($image_upl) {
		print qq|<form action="$registcgi" method="post" name="myFORM" enctype="multipart/form-data">\n|;
	} else {
		print qq|<form action="$registcgi" method="post" name="myFORM">\n|;
	}

	print <<EOM;
<input type="hidden" name="mode" value="edit_log">
<input type="hidden" name="job" value="edit2">
<input type="hidden" name="f" value="$in{'f'}">
<input type="hidden" name="no" value="$in{'no'}">
<input type="hidden" name="myjob" value="$myjob">
<input type="hidden" name="$mylog" value="1">
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>�薼</td>
  <td>
    <input type="text" name="sub" size="$sublength" value="$sub" maxlength="$sublength">
EOM
	print "    <input type=\"checkbox\" ";
	if ($is_sage eq '1') { print 'checked '; }
	print "disabled>sage\n";
	print <<EOM;
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>���O</td>
  <td><input type="text" name="name" size="30" value="$nam" maxlength="20"></td>
</tr>
EOM
	if ($user_id ne '') {
		print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>�o�^ID</td>
  <td><input type="text" size="30" value="$user_id" disabled></td>
</tr>
EOM
	}
	if ($history_id ne '') {
		print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>����ID</td>
  <td><input type="text" size="30" value="$history_id" disabled></td>
</tr>
EOM
	}
	if ($cookie_a ne '') {
		print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>CookieA</td>
  <td><input type="text" size="30" value="$cookie_a" disabled></td>
</tr>
EOM
	}
	if ($in_mail == 2) {
	} else {

	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80" nowrap>E-Mail</td>
  <td><input type="text" name="email" size="30" value="$eml">
EOM

	if ($show_mail) {
		print "  <select name=\"mvw\">\n";
		if ($cmvw eq "") { $cmvw = 0; }
	@mvw = ('��\��','�\��');
	foreach (0,1) {
		if ($mvw == $_) {
			print "<option value=\"$_\" selected>$mvw[$_]\n";
		} else {
			print "<option value=\"$_\">$mvw[$_]\n";
		}
	}
		print "</select>\n";
	} elsif ($usermail) {
		print "  <input type=\"hidden\" name=\"mvw\" value=\"0\"> ���͂���� <img src=\"$imgurl/mail.gif\" alt=\"���[���𑗐M����\" width=\"16\" height=\"13\" border=\"0\"> ���烁�[�����󂯎��܂��i�A�h���X��\\���j\n";
	}
	if ($in_mail == 3) {
		print " ���f���e�h�~�̂��߉��������Ɠ��e�ł��܂���\n";

	} elsif ($in_mail == 1) {
	print " �i�K�{�j\n";
	}
	print <<EOM;
</td>
</tr>
EOM

	}
	if ($url eq "") { $url = "http://"; }

	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80">URL</td>
  <td bgcolor="$col2"><input type="text" name="url" size="45" value="$url"></td>
</tr>
EOM

	# �Y�t�t�H�[��
	if ($image_upl) {
		print "<tr bgcolor=\"$col2\"><td bgcolor=\"$col2\" width=\"80\">�Y�t</td>";
		print "<td bgcolor=\"$col2\">\n";
		print "<input type=\"hidden\" name=\"increase_num\" value=\"1\">\n";

		my $max_num = $max_upl_num;
		my @imgs = (undef);
		foreach my $i (1 .. 6) {
			my @img = split(/,/, $upl{$i});
			push(@imgs, \@img);
			if ($i > $max_num && $img[0] ne '') {
				$max_num = $i;
			}
		}

		foreach my $i (1 .. $max_num) {
			print "<input type=\"file\" name=\"upfile$i\" size=\"45\"";
			if ($i > $max_upl_num) {
				print " disabled";
			}
			print ">\n";

			my ($img_folder_number, $ex) = @{$imgs[$i]};
			if ($ex) {
				print "&nbsp;[<a href=\"$upldir/$img_folder_number/$tim-$i$ex\" target=\"_blank\">�Y�t$i</a>]\n";
				print "<input type=\"checkbox\" name=\"del$i\" value=\"1\">�Y�t�폜\n";
			}
			print "<br>\n";
		}

		print "</td></tr>\n";
	}

	print <<EOM;
<tr bgcolor="$col2">
  <td bgcolor="$col2" width="80">�R�����g</td>
  <td bgcolor="$col2">
EOM

	# �A�C�R��
	if ($smile) {
		@s1 = split(/\s+/, $smile1);
		@s2 = split(/\s+/, $smile2);
		foreach (0 .. $#s1) {
			print "<a href=\"javascript:MyFace('$s2[$_]')\">";
			print "<img src=\"$imgurl/$s1[$_]\" border=0></a>\n";
		}
		print "<br>\n";
	}

	if ($myjob eq "admin") {
		print "<input type=hidden name=pass value=\"$in{'pass'}\">\n";
	} else {
		print "<input type=hidden name=pwd value=\"$in{'pwd'}\">\n";
	}

	$com =~ s/<br>/\n/g;
	print <<"EOM";
<textarea name="comment" cols="$cols" rows="$rows" wrap="soft">$com</textarea></td></tr>
EOM

if ($pw eq "") {
	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2"><br></td>
  <td bgcolor="$col2">
    ���̋L���ɂ̓p�X���[�h�͐ݒ肳��Ă��܂���</td>
</tr>
EOM

} elsif ($myjob eq "admin" && $clearpass || $myjob eq "user" && $in{'pwd'} eq $pass && $clearpass ) {
	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2"><br></td>
  <td bgcolor="$col2">
    <input type="checkbox" name="clearpass" value="1" checked>�L���̃p�X���[�h���N���A����</td>
</tr>
EOM
	}

	print <<"EOM";
<tr bgcolor="$col2">
  <td bgcolor="$col2"><br></td>
  <td bgcolor="$col2">
    <input type="submit" value="�L�����C������"></td>
  </form></tr></table>
</Td></Tr></Table>
</form></div>
</body>
</html>
EOM
	exit;
}



1;

