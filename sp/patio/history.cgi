#!/usr/bin/perl

# ���肵�܎� Web Patio v3.4 k1.00

#��������������������������������������������������������������������
#�� [ WebPatio �������ݗ���\��CGI ]
#�� history.cgi - based on patio.cgi 2011/04/08
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

BEGIN {
	# �O���t�@�C����荞��
	require './init.cgi';
	require $jcode;
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use NGThread;
use HistoryCookie;
use HistoryLog;

&parse_form;
if ($mode eq "check") {
	require $checkpl;
	&check;
}

&axscheck;
if ($mode eq "find") {
	require $findpl;
	&find;
}
elsif ($mode eq "enter_disp") { &enter_disp; }
elsif ($mode eq "logoff") { &logoff; }
elsif ($mode eq "ngthread_display_mode") { set_ngthread_display_mode(); }
elsif ($mode eq "ngthread_words") { set_ngthread_words(); }
elsif ($mode eq "delete_post_history" && $postflag) { delete_post_history(); }
&history_list_view;

#-------------------------------------------------
#  ���j���[���\��
#-------------------------------------------------
sub history_list_view {
	local($alarm,$i,$top);

	# �A���[������`
	$alarm = int ( $m_max * 0.9 );

	# ����ID���擾
	my $chistory_id = do {
		my $instance = HistoryCookie->new();
		$instance->get_history_id();
	};

	# ����ID���O�C���ς݂̏ꍇ�AHistoryLog�C���X�^���X��������
	my $history_log = defined($chistory_id) ? HistoryLog->new($chistory_id) : undef;

	# NG�X���b�h�ݒ�ǂݍ���
	my $ngthread = do {
		if (defined($history_log)) {
			# HistoryLog�C���X�^���X���������ς݂̏ꍇ�A����ID���O���g�p����悤������
			NGThread->new($history_log);
		} else {
			# ����ȊO�̏ꍇ�́ACookie���g�p����悤������
			NGThread->new();
		}
	};
	my $ngthread_display_mode = $ngthread->get_display_mode();

	&header();
	print <<"EOM";


<STYLE type="text/css">
<!--

*{
	margin:0px;
	padding:0px;
}





table#teeest{
  background-color:#ffffff;
/*  border: 1px solid #64bf64;	*/
  border-collapse: collapse;
  max-width:100%;
}

table#teeest tr{
/*  border: 1px solid #64bf64;	*/
}
table#teeest td {
  border-bottom: 1px solid #64bf64;
}

#wrapper-main-in-table{
	margin:20px;
}

blockquote{
	margin:10px 0px;
}


tr.test6 a,
tr.test2 a,
tr.test7 a,
tr.test1 a,	/* �Ǘ��҃��b�N */
tr.test3 a,	/* 	�X���b�h�������O�}�[�N */
tr.test5 a,
td.test5 a {
	display:block;
	width:100%;
	color:#000000 !important;
	padding:10px;
}

p.thread{
}
p.thread a:link,
p.thread a:visited{
	color:#888888;
	padding:8px 0px 8px 6px;
	display:block;
	text-decoration:none;
}
/*
p.thread a:visited{
	color:#ff8c00;
}
*/


.td1{
	border-bottom:1px solid #cbcbcb;
	width:100%;
}
.td2{
	border-bottom:1px solid #cbcbcb;
	background-color:#fafafa;
}

tr.ngthread { color: #e6e6e6; }
tr.ngthread a { color: #e6e6e6 !important; }

td.new_res_exists { color: #ff0000; }
tr.ngthread td.new_res_exists { color: #ffe5e5; }

#edit_toggle         { display: none; }
#edit_toggle:link    { color: #0000ff; }
#edit_toggle:visited { color: #0000ff; }
#edit_toggle:hover   { color: #0000ff; }
#edit_toggle::active { color: #0000ff; }
#edit_toggle.enabled { color: #ff0002; }
.edit_elements       { display: none; }

-->
</STYLE>


<div align="center">
<table width="95%" border="0">
<tr>
  <td>
	<table width="100%">
	<tr>
	<td><b style="font-size:$t_size; color:$t_color">$title</b><br>
<small>$desc</small></td><td align="right">
EOM

# Google AdSense
	&googleadsense;

	print <<"EOM";
</td>
EOM

	if ($authkey) {
		print "<td align=\"right\">�悤�����A<b>$my_name����</b></td>\n";
	}

	print <<EOM;
	</tr>
	</table>
  </td>
</tr>
<tr bgcolor="$col1">
  <td align="right" nowrap>
EOM

	if (!$createonlyadmin) {
	print <<EOM;
	<font color="$col2">|</font>
	<a href="$readcgi?mode=form"><font color="$col2">�V�K�X���b�h</font></a>
EOM
} else {
	print <<EOM;
	<font color="$col2">|</font>
	<font color="$col2">�X���b�h�쐬������</font>
EOM
}

	print <<EOM;
	<font color="$col2">|</font>
	<a href="$history_webprotect_issue_url" target="_top"><font color="$col2">��������ID���s�E�F��</font></a>
	<font color="$col2">|</font>
	<a href="$historycgi" target="_top"><font color="$col2">��������</font></a>
	<font color="$col2">|</font>
	<a href="$home" target="_top"><font color="$col2">�z�[���ɖ߂�</font></a>
	<font color="$col2">|</font>
	<a href="$notepage"><font color="$col2">���ӎ���</font></a>
	<font color="$col2">|</font>
	<a href="$bbscgi?mode=find"><font color="$col2">���[�h����</font></a>
	<font color="$col2">|</font>
	<a href="$readcgi?mode=past"><font color="$col2">�ߋ����O</font></a>
	<font color="$col2">|</font>
EOM

	# �F�؃��[�h�̂Ƃ�
	if ($authkey) {
		print "<a href=\"$bbscgi?mode=logoff\"><font color=\"$col2\">���O�I�t</font></a>\n";
		print "<font color=\"$col2\">|</font>\n";
	}

	print <<EOM;
	<a href="$admincgi"><font color="$col2">�Ǘ��p</font></a>
	<font color="$col2">|</font>&nbsp;&nbsp;&nbsp;
  </td>
</tr>
</table>
EOM

# �{����p���[�h

if ( $ReadOnly ) {
	print <<EOM;
<p>
<Table border=0 cellspacing=0 cellpadding=0 width="95%">
<Tr><Td>
<table border=0 cellspacing=1 cellpadding=5 width="100%">
<tr><td>
	<p align="left">$Oshirase</p>
</td>
</tr></table>
</Td></Tr></Table>
EOM

}

	my $edit_toggle_add_class_str = $in{'edit'} ? ' class="enabled"' : '';
	print <<EOM;
<form action="$historycgi" method="post">
<input type="hidden" name="mode" value="delete_post_history">
<br>
<h1>�������ݗ���</h1>
<br>
<a href="#" id="edit_toggle"$edit_toggle_add_class_str>�ҏW����</a><br><br>
<span class="edit_elements">
    <button type="button" id="edit_all_select">���ׂđI��</button>&nbsp;&nbsp;&nbsp;&nbsp;
    <input type="submit" value="�I�������X���b�h���폜"><br><br>
</span>

<Table border="0" cellspacing="0" cellpadding="0" id="index_table">
<Tr><Td>
<table id="teeest" border="0" cellspacing="0" cellpadding="5" width="100%">
<tr bgcolor="#bfecbf" class="thth">
  <td bgcolor="#bfecbf" class="center">�W�����v</td>
  <td bgcolor="#bfecbf" class="">�X���b�h��</td>
  <td bgcolor="#bfecbf" class="center">�V����</td>
  <td bgcolor="#bfecbf" class="center">���X��</td>
EOM

	if ($p eq "") { $p = 0; }
	$i = 0;

	# �������ݗ������O�\�� (����ID���O�C���Ϗ�Ԃ̏ꍇ�̂�)
	if (defined($history_log)) {
		# ���݂���X���b�h�����擾
		my @post_history = @{$history_log->get_post_histories()};

		# ���݂���X���b�h�ŁA�\���Ώۂł���΃X���b�h�����o��
		foreach my $thread_info_array_ref (@post_history) {
			# �����L�^���_�X���b�h���擾
			my ($thread_no, $res_no, $res_time) = @{$thread_info_array_ref};

			# �X���b�h���O�t�@�C���p�X����
			my $logfile_path = get_logfolder_path($thread_no) . "/$thread_no.cgi";

			# �X���b�h���O�t�@�C�����J���邩�ǂ���
			if (-r $logfile_path) {
				# �J�e�S���\���@�\ ������
				# �\���͈͊O�̏ꍇ�̓X�L�b�v
				if ($in{'k'} eq '' && ($i < $p || $i > $p + $history_display_menu - 1)) {
					$i++; # ���݃X���b�h���C���N�������g
					next;
				}

				# �X���b�h���擾
				open(my $log_fh, '<', $logfile_path) || error("Open Error: $thread_no.cgi");
				flock($log_fh, 1) || error("Lock Error: $thread_no.cgi");
				my $log_top = <$log_fh>;
				close($log_fh);
				chomp($log_top);
				my ($thread_creator_name, $sub, $res_count) = (split(/<>/, $log_top))[0..2];
				if ($res_count == 0) { $res_count = 1; } # �X���b�h�쐬�����0�ɂȂ��Ă��邽�߁A1�Ƃ���
				$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜
				my $orig_sub = $sub; # �X���b�h�^�C�g����ʓr�ۊ�

				# �J�e�S���\���@�\ �L����
				# �^�C�g�������ɃJ�e�S�������܂܂Ȃ����A�\���͈͊O�̏ꍇ�̓X�L�b�v
				if ($in{'k'} ne '' && ((my $no_cat_match = $sub !~ /$in{'k'}$/) || ($i < $p || $i > $p + $history_display_menu - 1))) {
					if (!$no_cat_match) {
						# �J�e�S�������܂݁A�\���͈͊O�̏ꍇ�̂�
						# ���݃X���b�h���C���N�������g
						$i++;
					}
					next;
				}

				# NG�X���b�h��v����
				my $is_ngthread = 0;
				if ($ngthread->is_ng_thread_creator($thread_creator_name) || $ngthread->is_ng_thread_title($orig_sub)) {
					# ��v����ꍇ
					if ($ngthread_display_mode == NGThread::DisplayMode_Hide) {
						# �X���b�h��\���̏ꍇ�̓X�L�b�v
						$i++; # ���݃X���b�h���C���N�������g
						next;
					} else {
						# �X���b�h���u���̏ꍇ�͒u��������
						$is_ngthread = 1;
					}
				}

				# �V�����X�����Z�o
				my $new_res_count = $res_count - $res_no;

				# �X���b�h ���X�\���͈͌���
				my $x = ($res_count - 20) >= 0 ? ($res_count - 20) : 0;
				my $y = $res_count + 20;

				if ($key eq '0' || $key == 4) { $icon = 'fold3.gif';$test = 'test1';$test_td = 'test1_td';$locked = '�y���b�N���z'; }
				elsif ($key == 2) { $icon = 'look.gif';$test = 'test7';$test_td = 'test7_td';$locked = ''; }
				elsif ($key == 3) { $icon = 'faq.gif';$test = 'test2';$test_td = 'test2_td';$locked = ''; }
				elsif ($res >= $alarm) { $icon = 'fold5.gif';$test = 'test3';$test_td = 'test1_td';$locked = ''; }
				elsif ($upl) { $icon = 'fold1.gif';$test = 'test5';$test_td = 'test4_td';$locked = ''; }
				elsif (time < $restime + $hot) { $icon = 'fold1.gif';$test = 'test5';$test_td = 'test5_td';$locked = ''; }
				else { $icon = 'fold1.gif';$test = 'test6';$test_td = 'test6_td';$locked = ''; }

				if ($is_ngthread) {
					# NG�X���b�h�̏ꍇ
					print "<tr class=\"$test ngthread\">";
				} else {
					print "<tr class=\"$test\">";
				}
				print "<td width=\"30\">";
				print "<p class=\"thread\"><a href=\"$readcgi?no=$thread_no#re\">>></a></p>";
				print "</td>";
				if ($is_ngthread) {
					# NG�X���b�h�̏ꍇ
					print "<td width=\"\"><a href=\"$readcgi?no=$thread_no\">---</a></td>";
				} else {
					print "<td width=\"\"><a href=\"$readcgi?no=$thread_no\">$sub</a></td>";
				}
				if ($new_res_count > 0) {
					# �V�����X��1���ȏ゠��ꍇ
					print "<td align=\"center\" width=\"70px\" class=\"new_res_exists\">\n";
				} else {
					print "<td align=\"center\" width=\"70px\">\n";
				}
					print <<"EOM";
<input type=\"checkbox\" name=\"thread_no\" value=\"$thread_no\" class=\"edit_elements edit_checkbox\">
$new_res_count
</td>
EOM
				print "<td align=\"center\" width=\"70px\"><a href=\"$readcgi?no=$thread_no&l=$x-$y#$res_count\">$res_count</a></td>";
				print "</tr>";

				$i++; # ���݃X���b�h���C���N�������g
			}
		}
	}

	print "</table></Td></Tr></Table>\n";
	print "</form>\n";


	# �y�[�W�ړ��{�^���\��
	if ($p - $history_display_menu >= 0 || $p + $history_display_menu < $i) {
		print "<br><br><table>\n";

		# ���ݕ\���y�[�W/�S�y�[�W���\��
		my $pages = int(($i - 1) / $history_display_menu) + 1; # �S�y�[�W���擾
		if ($p < 0) {
			# �}�C�i�X���w�肳�ꂽ���́A1�y�[�W�ڂƂ���
			$p = 0;
		} elsif ($p + 1 > $i) {
			# �S�X���b�h�������傫���l���w�肳�ꂽ���́A�ŏI�y�[�W�w��Ƃ���
			$p = ($pages - 1) * $history_display_menu;
		}
		my $current_page = int($p / $history_display_menu) + 1; # ���ݕ\���y�[�W�擾
		print "<tr><td class=\"num\" align=\"center\">$current_page/$pages</td></tr>\n";

		# 1�y�[�W�ځE�O��y�[�W�E�ŏI�y�[�W�ւ̃����N
		my $k_html = exists($in{k}) ? "k=$in{k}&" : '';
		print "<tr><td class=\"num\">";
		if ($current_page <= 1) {
			print "&lt;&lt;�@�O�ց@";
		} else {
			my $prev_page = ($current_page - 2) * $history_display_menu;
			print "<a href=\"$historycgi?${k_html}p=0\">&lt;&lt;</a>�@<a href=\"$historycgi?${k_html}p=$prev_page\">�O��</a>�@";
		}
		if ($current_page >= $pages) {
			print "���ց@&gt;&gt;";
		} else {
			my $next_page = $current_page * $history_display_menu;
			my $last_page = ($pages - 1) * $history_display_menu;
			print "<a href=\"$historycgi?${k_html}p=$next_page\">����</a>�@<a href=\"$historycgi?${k_html}p=$last_page\">&gt;&gt;</a>";
		}
		print "</td></tr>\n";

		print "</table>\n";
	}

	# ���쌠�\���i�폜�s�j

	# NG�X���b�h�\�����[�h�擾
	my $ngthread_display_mode_text = do {
		if ($ngthread_display_mode == NGThread::DisplayMode_Hide) {
			'�X���b�h���\��';
		} else {
			'�X���b�h����u��';
		}
	};
	# �X���b�h�쐬�҂�NG�ݒ���擾
	my $ngthread_ng_thread_creator = $ngthread->get_ng_thread_creator();
	# �X���b�h����NG�ݒ���擾
	my $ngthread_ng_thread_title = $ngthread->get_ng_thread_title();
	# �X���b�h����NG�̏��O�ݒ���擾
	my $ngthread_ng_thread_title_exclude = $ngthread->get_ng_thread_title_exclude();
	print <<"EOM";
<br><br>

<!-- NG�X���b�h�ݒ� -->
<blockquote style="background-color:#e6e6e6">
<form action="$historycgi" method="post">
<input type="hidden" name="mode" value="ngthread_display_mode">
<br>
<b>�ENG�X���b�h�\\���ݒ�</b><br>
���݂�NG�X���b�h�\\���ݒ�́u$ngthread_display_mode_text�v�ł��B<br>

<input type="radio" name="display_mode" value="0" id="ngthread_display_hide" required> <label for="ngthread_display_hide">�X���b�h���\\���ɂ���</label>&nbsp;&nbsp;
<input type="radio" name="display_mode" value="1" id="ngthread_display_replace"> <label for="ngthread_display_replace">�X���b�h����u������</label>
<p><input type="submit" value="�@�ݒ肷��@"></p>
</form>
<br><br>
<form action="$historycgi" method="post">
<input type="hidden" name="mode" value="ngthread_words">
<b>�X���b�h�쐬�҂�NG�ݒ�</b><br>
<textarea name="ng_thread_creator" rows="10" cols="40">$ngthread_ng_thread_creator</textarea>
<br><br>
<b>�X���b�h����NG�ݒ�</b><br>
<textarea name="ng_thread_title" rows="10" cols="40">$ngthread_ng_thread_title</textarea>
<br><br>
<b>�X���b�h����NG�̏��O�ݒ�</b><br>
<textarea name="ng_thread_title_exclude" rows="10" cols="40">$ngthread_ng_thread_title_exclude</textarea>
<p><input type="submit" value="�@�ݒ肷��@"></p>
</form>
</blockquote><!-- end of blockquote -->


<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2"><td bgcolor="$col2" align="center">
<img src="$imgurl/foldnew.gif"> �V�����������݂̂���X���b�h &nbsp;&nbsp;
<img src="$imgurl/fold1.gif" alt="�W���X���b�h"> �W���X���b�h &nbsp;&nbsp;
<img src="$imgurl/fold6.gif" alt="�Y�t����"> �Y�t���� &nbsp;&nbsp;
<img src="$imgurl/fold3.gif" alt="���b�N��"> ���b�N���i�����s�j&nbsp;&nbsp;
<img src="$imgurl/fold5.gif" alt="�A���[��"> �A���[���i�ԐM��$alarm���ȏ�j&nbsp;&nbsp;
<img src="$imgurl/faq.gif"> �e�`�p�X���b�h&nbsp;&nbsp;
<img src="$imgurl/look.gif" alt="�Ǘ��҃��b�Z�[�W"> �Ǘ��҃��b�Z�[�W
</td></tr></table></Td></Tr></Table><br><br>
<!-- ���쌠�\\�����E�폜�֎~ ($ver) -->
<span class="s1">
- <a href="http://www.kent-web.com/" target="_top">Web Patio</a> -
 <a href="http://kirishima.it/patio/" target="_top">���肵�܎�</a> -
</span></div>
</body>
</html>
EOM

	# HistoryLog�C���X�^���X���
	if (defined($history_log)) {
		$history_log->DESTROY();
	}

	exit;
}

#-------------------------------------------------
#  URL�G���R�[�h
#-------------------------------------------------
sub url_enc {
	local($_) = @_;

	s/(\W)/'%' . unpack('H2', $1)/eg;
	s/\s/+/g;
	$_;
}

#-------------------------------------------------
#  ���O�I�t
#-------------------------------------------------
sub logoff {
	if ($my_ckid =~ /^\w+$/) {
		unlink("$sesdir/$my_ckid.cgi");
	}
	print "Set-Cookie: patio_member=;\n";

	&enter_disp;
}

#-------------------------------------------------
#  NG�X���b�h�\���ݒ�
#-------------------------------------------------
sub set_ngthread_display_mode {
	my $value = int($in{'display_mode'});

	# ���͒l�`�F�b�N
	if ($value != NGThread::DisplayMode_Hide && $value != NGThread::DisplayMode_Replace) {
		error("�s���Ȓl�ł�");
	}

	# Cookie�ۑ�
	my $ngthread = NGThread->new();
	$ngthread->set_display_mode($value);
	$ngthread->save();

	# ������ʕ\��
	if ($value == NGThread::DisplayMode_Hide) {
		success('�u�X���b�h���\���v�ɐݒ肵�܂����B', $historycgi);
	} else {
		success('�u�X���b�h����u���v�ɐݒ肵�܂����B', $historycgi);
	}
	exit;
}

#-------------------------------------------------
#  NG�X���b�h���[�h�ݒ�
#-------------------------------------------------
sub set_ngthread_words {
	# �l���Z�b�g
	my $ngthread = NGThread->new();
	$ngthread->set_ng_thread_creator($in{'ng_thread_creator'});             # �X���b�h�쐬�҂�NG�ݒ�
	$ngthread->set_ng_thread_title($in{'ng_thread_title'});                 # �X���b�h����NG�ݒ�
	$ngthread->set_ng_thread_title_exclude($in{'ng_thread_title_exclude'}); # �X���b�h����NG�̏��O�ݒ�

	# Cookie�ۑ�
	$ngthread->save();

	# ������ʕ\��
	success('NG�X���b�h���[�h�ɐݒ肵�܂����B', $historycgi);
	exit;
}

#-------------------------------------------------
#  �������݃X���b�h�����폜
#-------------------------------------------------
sub delete_post_history {
	# ����ID���擾
	my $chistory_id = do {
		my $instance = HistoryCookie->new();
		$instance->get_history_id();
	};
	if ($chistory_id eq '') {
		# ����ID���擾�ł��Ȃ����͏������ݗ����y�[�W�ɋ����ړ�
		print "Location: $historycgi\n\n";
		exit;
	}

	# �폜����X���b�h�ԍ���1�ȏ゠�鎞�A�������ݗ������O���J���č폜����
	my @delete_thread_no_array = map { int($_) } split("\0", $in{'thread_no'}); # �폜����X���b�h�ԍ����擾
	if (scalar(@delete_thread_no_array) > 0) {
		# HistoryLog�C���X�^���X��������
		my $history_log = HistoryLog->new($chistory_id);

		# �������݃X���b�h�������폜
		$history_log->delete_post_histories(\@delete_thread_no_array);

		# HistoryLog�C���X�^���X���
		$history_log->DESTROY();
	}

	# �������b�Z�[�W�\��
	&header if (!$headflag);
	print <<"EOM";
<div align="center">
<p>�X���b�h���폜���܂����B</p>
<p>
<input type="button" value="�O��ʂɂ��ǂ�" onclick="location.href='$historycgi?edit=1'">
</div>
</body>
</html>
EOM
	exit;
}
