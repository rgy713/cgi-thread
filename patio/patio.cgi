#!/usr/bin/perl

# ���肵�܎� Web Patio v3.4 k1.00
$kver ="1.00";
# 2011/07/04 �\�[�X�R�[�h��3.4������
# 2011/04/27 �\�[�X�R�[�h��3.31������
# 2010/11/14 �X���b�h�ԍ��̕\�����I�v�V�����őI�ׂ�悤��
# 2009/10/25 �������啶������������ʂ��Ȃ�
# 2009/07/01 �摜��\���e�X�g
# 2009/04/07 �ߋ����O�\������URL��ύX
# 2009/03/14 �X���b�h�쐬�������[�h�̒ǉ�
# 0.74 2008/08/29 ��������ꎮ�A�[�J�C�u���X�V
# 0.70 2008/02/27 �X���b�h�����@�\�𑕔��i�����ɂ͎w�背�X�ȍ~���R�s�[���ĐV�K�X���b�h�쐬�j
# 0.33 2007/05/19 �f���̐�����ǉ�
# 0.30 2007/01/22 ����

#��������������������������������������������������������������������
#�� [ WebPatio ]
#�� patio.cgi - 2011/04/08
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# �O���t�@�C����荞��
BEGIN {
	require './init.cgi';
	require $jcode;
}
use lib qw(./lib ./lib/perl5);
use lib qq($history_webprotect_dir/lib);
use ThreadUpdateLogDB;
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
elsif ($mode eq "feed") { &rssfeed; }
elsif ($mode eq "ngthread_display_mode") { set_ngthread_display_mode(); }
elsif ($mode eq "ngthread_words") { set_ngthread_words(); }
&list_view;

#-------------------------------------------------
#  ���j���[���\��
#-------------------------------------------------
sub list_view {
	local($alarm,$i,$top);

	# �A���[������`
	$alarm = int ( $m_max * 0.9 );

	# NG�X���b�h�ݒ�ǂݍ���
	my $ngthread = do {
		if (defined(my $chistory_id = HistoryCookie->new()->get_history_id())) {
			# ����ID���O�C���ς݂̏ꍇ�A����ID���O���g�p����悤������
			NGThread->new(HistoryLog->new($chistory_id));
		} else {
			# ����ȊO�̏ꍇ�́ACookie���g�p����悤������
			NGThread->new();
		}
	};
	my $ngthread_display_mode = $ngthread->get_display_mode();
	$ngthread->DESTROY();

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



-->
</STYLE>


<div align="center">
<table width="95%" border="0" height="50px" style="padding:10px;">
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
	<a href="$webprotect_path/index.html" target="_top"><font color="$col2">�o�^ID���s</font></a>
	<font color="$col2">|</font>
	<a href="$history_webprotect_issue_url" target="_top"><font color="$col2">����ID���s�E�F��</font></a>
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

	print <<EOM;
<p>

<Table border="0" cellspacing="0" cellpadding="0" id="index_table">
<Tr><Td>
<table id="teeest" border="0" cellspacing="0" cellpadding="5" width="100%">
<tr bgcolor="#bfecbf" class="thth">
  <td bgcolor="#bfecbf" class="center">�W�����v</td>
  <td bgcolor="#bfecbf" class="">�X���b�h��</td>
  <td bgcolor="#bfecbf" class="center">��</td>
  <td bgcolor="#bfecbf" class="center">����</td>
EOM

	# �X���\��
	if ($p eq "") { $p = 0; }
	$i = 0;
	# �J�e�S���\���@�\�̗L����Ԃɂ���ď�������ύX���邽�߁A
	# ���O�ǂݎ�莞�̊e�������T�u���[�`��������
	my $countLog = sub {
		# �Ώۃ��O�Ƃ��Č����J�E���g���A�\���ΏۊO�̏ꍇ�X�L�b�v����
		$i++;
		next if ($i < $p + 1);
		last if ($i > $p + $menu1);
	};
	my $readLog = sub {
		# ���O��ǂݎ��A�e���ڂ�ϐ��ɑ�����ă��X�g�ŕԂ�
		chomp($_);
		($num,$sub,$res,$nam,$date,$na2,$key,$upl,$ressub,$restime) = split(/<>/);
		$sub =~ s/\0*//g; # ���������΍�Ƃ��āA�^�C�g���Ɋ܂܂�Ă���null����(\0)���폜
		$orig_sub = $sub; # �X���b�h�^�C�g����ʓr�ۊ�
	};
	my $judgeCategory = sub {
		next if $sub !~ /$in{'k'}$/; # �^�C�g�������ɃJ�e�S�������܂܂Ȃ��ꍇ�̓X�L�b�v����
	};
	open(IN,"$nowfile") || &error("Open Error: $nowfile");
	$top = <IN>;
	while (<IN>) {
		local ($num,$sub,$res,$nam,$date,$na2,$key,$upl,$ressub,$restime,$orig_sub);

		# ���O�ǂݎ�菈�����s
		if ($in{'k'} eq '') {
			# �J�e�S���\���@�\ ������
			$countLog->();
			$readLog->();
		} else {
			# �J�e�S���\���@�\ �L����
			$readLog->();
			$judgeCategory->();
			$countLog->();
		}

		# NG�X���b�h��v����
		my $is_ngthread = 0;
		if ($ngthread->is_ng_thread_creator($nam) || $ngthread->is_ng_thread_title($orig_sub)) {
			# ��v����ꍇ
			if ($ngthread_display_mode == NGThread::DisplayMode_Hide) {
				# �X���b�h��\���̏ꍇ�̓X�L�b�v
				next;
			} else {
				# �X���b�h���u���̏ꍇ�͒u��������
				$is_ngthread = 1;
			}
		}

		if ($key eq '0' || $key == 4) { $icon = 'fold3.gif';$test = 'test1';$test_td = 'test1_td';$locked = '�y���b�N���z'; }
		elsif ($key == 2) { $icon = 'look.gif';$test = 'test7';$test_td = 'test7_td';$locked = ''; }
		elsif ($key == 3) { $icon = 'faq.gif';$test = 'test2';$test_td = 'test2_td';$locked = ''; }
		elsif ($res >= $alarm) { $icon = 'fold5.gif';$test = 'test3';$test_td = 'test1_td';$locked = ''; }
		elsif ($upl) { $icon = 'fold1.gif';$test = 'test5';$test_td = 'test4_td';$locked = ''; }
		elsif (time < $restime + $hot) { $icon = 'fold1.gif';$test = 'test5';$test_td = 'test5_td';$locked = ''; }
		else { $icon = 'fold1.gif';$test = 'test6';$test_td = 'test6_td';$locked = ''; }

		if($nam eq "" || $sub eq ""){}
		else{
		print "<tr class=\"$test";
		if ($is_ngthread) {
			print " ngthread";
		}
		print "\">";
		print "<td width=\"30\">";
		print "<p class=\"thread\"><a href=\"$readcgi?no=$num#re\">>></a></p>";
		print "</td>";
		if ($is_ngthread) {
			print "<td width=\"\"><a href=\"$readcgi?no=$num\">---</a></td>";
		} else {
			print "<td width=\"\"><a href=\"$readcgi?no=$num\">$sub</a></td>";
		}
		print "<td align=\"center\" width=\"70px\">$res</td>";

		$date =~ s/([0-9][0-9]:[0-9][0-9]):[0-9][0-9].*/\1/g;
		print "<td align=\"center\" width=\"150px\">$date</td>";
		print "</tr>";
		}
	}
	# �c��̕\���͈͊O�̃X���b�h�����J�E���g
	if ($in{'k'} eq '') {
		# �J�e�S���\���@�\�������̓o�b�t�@�Ɉ�Ăɓǂݍ��݉��s���J�E���g
		local $/ = undef;
		my $buffer = <IN>;
		$i += ($buffer =~ tr/\n//);
	} else {
		# �L������1�s���^�C�g����������v���邩�m�F���ăJ�E���g
		while(<IN>) {
			chomp($_);
			(my $sub = (split(/<>/))[1]) =~ s/\0*//g;
			$i++ if $sub =~ /$in{'k'}$/;
		}
	}
	close(IN);

	print "</table></Td></Tr></Table>\n";


	# �y�[�W�ړ��{�^���\��
	if ($p - $menu1 >= 0 || $p + $menu1 < $i) {
		print "<br><br><table>\n";

		# ���ݕ\���y�[�W/�S�y�[�W���\��
		my $pages = int(($i - 1) / $menu1) + 1; # �S�y�[�W���擾
		if ($p < 0) {
			# �}�C�i�X���w�肳�ꂽ���́A1�y�[�W�ڂƂ���
			$p = 0;
		} elsif ($p + 1 > $i) {
			# �S�X���b�h�������傫���l���w�肳�ꂽ���́A�ŏI�y�[�W�w��Ƃ���
			$p = ($pages - 1) * $menu1;
		}
		my $current_page = int($p / $menu1) + 1; # ���ݕ\���y�[�W�擾
		print "<tr><td class=\"num\" align=\"center\">$current_page/$pages</td></tr>\n";

		# 1�y�[�W�ځE�O��y�[�W�E�ŏI�y�[�W�ւ̃����N
		my $k_html = exists($in{k}) ? "k=$in{k}&" : '';
		print "<tr><td class=\"num\">";
		if ($current_page <= 1) {
			print "&lt;&lt;�@�O�ց@";
		} else {
			my $prev_page = ($current_page - 2) * $menu1;
			print "<a href=\"$bbscgi?${k_html}p=0\">&lt;&lt;</a>�@<a href=\"$bbscgi?${k_html}p=$prev_page\">�O��</a>�@";
		}
		if ($current_page >= $pages) {
			print "���ց@&gt;&gt;";
		} else {
			my $next_page = $current_page * $menu1;
			my $last_page = ($pages - 1) * $menu1;
			print "<a href=\"$bbscgi?${k_html}p=$next_page\">����</a>�@<a href=\"$bbscgi?${k_html}p=$last_page\">&gt;&gt;</a>";
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
#  RSS(2.0)�t�B�[�h
#-------------------------------------------------
sub rssfeed {

	if ($in{'no'} ne "") {

		# �X���b�h�ǂݍ���
		open(IN,"$logdir/$in{'no'}.cgi") || &error("Open Error: $logdir/$in{'no'}.cgi");
		eval "flock(IN, 1);";
		my $top = <IN>;

		# �t�@�C���|�C���^�L��
		my $toptell = tell(IN);

		# �e�L������RSS�w�b�_����
		while (<IN>) {
			my($no2,$sub,$nam,$tim) = (split(/<>/))[0,1,2,11];

			print "Content-type: text/xml\n\n";

			print '<?xml version="1.0" encoding="uft-8"?>'."\n";
			print '<rss version="2.0" xml:lang="ja">'."\n";
			print "<channel>\n\n";
			print "<title>PokemonStyle11111</title>\n\n";

			print "<title>[$in{'no'}] $sub - $title</title>\n";
			print "<link>$rss_readcgi?no=$in{'no'}</link>\n";
			print "<description>$desc</description>\n\n";

			last;
		}

		# �|�C���^����
		seek(IN,$toptell,0);

		# �V�����ŕ\��
		my $i = 0;
		my @art = <IN>;
		@art = reverse(@art);

		foreach (@art) {
			$i++; last if ($t_max < $i);
			chomp;
			my($no2,$sub,$nam,$com,$tim) = (split(/<>/))[0,1,2,4,11];

			# ���e�����𐮌`
			my @ltime = split(/\s+/,localtime($tim));
			my $rsstime = "$ltime[0], $ltime[2] $ltime[1] $ltime[4] $ltime[3] +0900";

			# ���̎Q�Ɩ�����
			$com =~ s/&/&amp;/g;

			# ���s���T�j�^�C�W���O�EBBCode�폜
			$com =~ s/<br>/&lt;br \/&gt;/g;
			$com =~ s/\[b\](.*?)\[\/b\]/$1/ig;
			$com =~ s/\[i\](.*?)\[\/i\]/$1/ig;
			$com =~ s/\[u\](.*?)\[\/u\]/$1/ig;
			$com =~ s/\[s\](.*?)\[\/s\]/$1/ig;
			$com =~ s/\[code\](.*?)\[\/code\]/$1/ig;
			$com =~ s/\[url=((?:htt|ft)ps?\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]+)\](.*?)\[\/url\]/$1/ig;
			$com =~ s/\[color=(\#[0-9A-F]{6}|[A-Z]+)\](.*?)\[\/color\]/$2/ig;

			# �e�L���̏ꍇ�͔ԍ����w�肵�Ȃ�
			my $resnum = ''; $resnum = "&amp;l=$no2" if ($no2 != 0);

			# �A�C�e���\��
			print "<item>\n";
			print "<title>$sub ( $no2 ) by $nam</title>\n";
			print "<link>$rss_readcgi?no=$in{'no'}$resnum</link>\n";
			print "<description>&lt;p&gt;$com&lt;/p&gt;</description>\n";
			print "<pubDate>$rsstime</pubDate>\n";
			print "</item>\n\n";
		}

		close(IN);

	} else {

		# index�ǂݍ���
		open(IN,"$nowfile") || &error("Open Error: $nowfile");
		eval "flock(IN, 1);";

		print "Content-type: text/xml\n\n";

		# RSS�w�b�_
		print <<"EOM";
<?xml version="1.0" encoding="shift-jis"?>
<rss version="2.0" xml:lang="ja">
<channel>
<title>WebPatio</title>
EOM

		my $i = 0;
		my $top = <IN>;

		while (<IN>) {
			chomp;
			my($num,$sub,$date,$na2,$key,$ressub,$restime) = (split(/<>/))[0,1,4,5,6,8,9];

			#TODO 20171027
			#�X���b�h�^�C�g�����ݒ�l�ɒ��Ԉ�v�ō��v����X���b�h�́ARSS�ipatio.cgi?mode=feed�̈ꗗ�j�ɏo�͂��܂���B
			my $is_continue = 'false';
			foreach my $no_word (@rss_no_word) {
				my $no_word_decode = $enc_cp932->decode($no_word);
				if($no_word ne '' && $enc_cp932->decode($sub) =~ /$no_word_decode/){
					$is_continue = 'true';
					last;
				}
			}
			if($is_continue eq 'true'){
				next;
			}

			next if ($key == 6);
			$i++; last if ($menu1 < $i);

			# ���̎Q�Ɩ�����
			$ressub =~ s/&/&amp;/g;
			$na2 =~ s/&/&amp;/g;

			# ���e�����𐮌`
			my @ltime = split(/\s+/,localtime($restime));
			my $rsstime = "$ltime[0], $ltime[2] $ltime[1] $ltime[4] $ltime[3] +0900";

			# �A�C�e���\��
			print "<item>\n";
			print "<title>$sub</title>\n";
			print "<link>$rss_readcgi?no=$num</link>\n";
			print "<description>&lt;b&gt;$ressub&lt;/b&gt; by $na2 $date</description>\n";
			print "<pubDate>$rsstime</pubDate>\n";
			print "</item>\n\n";
		}

		close(IN);

	}

	print "</channel>\n</rss>";
	exit;
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

	# ����ID���O/Cookie�ۑ�
	my $ngthread = do {
		if (defined(my $chistory_id = HistoryCookie->new()->get_history_id())) {
			# ����ID���O�C���ς݂̏ꍇ�A����ID���O���g�p����悤������
			NGThread->new(HistoryLog->new($chistory_id));
		} else {
			# ����ȊO�̏ꍇ�́ACookie���g�p����悤������
			NGThread->new();
		}
	};
	$ngthread->set_display_mode($value);
	$ngthread->save();
	$ngthread->DESTROY();

	# ������ʕ\��
	if ($value == NGThread::DisplayMode_Hide) {
		success('�u�X���b�h���\���v�ɐݒ肵�܂����B', $bbscgi);
	} else {
		success('�u�X���b�h����u���v�ɐݒ肵�܂����B', $bbscgi);
	}
	exit;
}

#-------------------------------------------------
#  NG�X���b�h���[�h�ݒ�
#-------------------------------------------------
sub set_ngthread_words {
	# �l���Z�b�g
	my $ngthread = do {
		if (defined(my $chistory_id = HistoryCookie->new()->get_history_id())) {
			# ����ID���O�C���ς݂̏ꍇ�A����ID���O���g�p����悤������
			NGThread->new(HistoryLog->new($chistory_id));
		} else {
			# ����ȊO�̏ꍇ�́ACookie���g�p����悤������
			NGThread->new();
		}
	};
	$ngthread->set_ng_thread_creator($in{'ng_thread_creator'});             # �X���b�h�쐬�҂�NG�ݒ�
	$ngthread->set_ng_thread_title($in{'ng_thread_title'});                 # �X���b�h����NG�ݒ�
	$ngthread->set_ng_thread_title_exclude($in{'ng_thread_title_exclude'}); # �X���b�h����NG�̏��O�ݒ�

	# Cookie�ۑ�
	$ngthread->save();

	# NGThread HistoryLog�C���X�^���X���
	$ngthread->DESTROY();

	# ������ʕ\��
	success('NG�X���b�h���[�h�ɐݒ肵�܂����B', $bbscgi);
	exit;
}
