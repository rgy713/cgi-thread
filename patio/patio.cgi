#!/usr/bin/perl

# きりしま式 Web Patio v3.4 k1.00
$kver ="1.00";
# 2011/07/04 ソースコードを3.4相当に
# 2011/04/27 ソースコードを3.31相当に
# 2010/11/14 スレッド番号の表示をオプションで選べるように
# 2009/10/25 検索時大文字小文字を区別しない
# 2009/07/01 画像非表示テスト
# 2009/04/07 過去ログ表示時のURLを変更
# 2009/03/14 スレッド作成制限モードの追加
# 0.74 2008/08/29 いったん一式アーカイブを更新
# 0.70 2008/02/27 スレッド分割機能を装備（厳密には指定レス以降をコピーして新規スレッド作成）
# 0.33 2007/05/19 掲示板の説明を追加
# 0.30 2007/01/22 着手

#┌─────────────────────────────────
#│ [ WebPatio ]
#│ patio.cgi - 2011/04/08
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

# 外部ファイル取り込み
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
#  メニュー部表示
#-------------------------------------------------
sub list_view {
	local($alarm,$i,$top);

	# アラーム数定義
	$alarm = int ( $m_max * 0.9 );

	# NGスレッド設定読み込み
	my $ngthread = do {
		if (defined(my $chistory_id = HistoryCookie->new()->get_history_id())) {
			# 書込IDログイン済みの場合、書込IDログを使用するよう初期化
			NGThread->new(HistoryLog->new($chistory_id));
		} else {
			# それ以外の場合は、Cookieを使用するよう初期化
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
tr.test1 a,	/* 管理者ロック */
tr.test3 a,	/* 	スレッド落ち寸前マーク */
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
		print "<td align=\"right\">ようこそ、<b>$my_nameさん</b></td>\n";
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
	<a href="$readcgi?mode=form"><font color="$col2">新規スレッド</font></a>
EOM
} else {
	print <<EOM;
	<font color="$col2">|</font>
	<font color="$col2">スレッド作成制限中</font>
EOM
}

	print <<EOM;
	<font color="$col2">|</font>
	<a href="$webprotect_path/index.html" target="_top"><font color="$col2">登録ID発行</font></a>
	<font color="$col2">|</font>
	<a href="$history_webprotect_issue_url" target="_top"><font color="$col2">書込ID発行・認証</font></a>
	<font color="$col2">|</font>
	<a href="$historycgi" target="_top"><font color="$col2">書込履歴</font></a>
	<font color="$col2">|</font>
	<a href="$home" target="_top"><font color="$col2">ホームに戻る</font></a>
	<font color="$col2">|</font>
	<a href="$notepage"><font color="$col2">留意事項</font></a>
	<font color="$col2">|</font>
	<a href="$bbscgi?mode=find"><font color="$col2">ワード検索</font></a>
	<font color="$col2">|</font>
	<a href="$readcgi?mode=past"><font color="$col2">過去ログ</font></a>
	<font color="$col2">|</font>
EOM

	# 認証モードのとき
	if ($authkey) {
		print "<a href=\"$bbscgi?mode=logoff\"><font color=\"$col2\">ログオフ</font></a>\n";
		print "<font color=\"$col2\">|</font>\n";
	}

	print <<EOM;
	<a href="$admincgi"><font color="$col2">管理用</font></a>
	<font color="$col2">|</font>&nbsp;&nbsp;&nbsp;
  </td>
</tr>
</table>
EOM

# 閲覧専用モード

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
  <td bgcolor="#bfecbf" class="center">ジャンプ</td>
  <td bgcolor="#bfecbf" class="">スレッド名</td>
  <td bgcolor="#bfecbf" class="center">数</td>
  <td bgcolor="#bfecbf" class="center">時間</td>
EOM

	# スレ表示
	if ($p eq "") { $p = 0; }
	$i = 0;
	# カテゴリ表示機能の有効状態によって処理順を変更するため、
	# ログ読み取り時の各処理をサブルーチン化する
	my $countLog = sub {
		# 対象ログとして件数カウントし、表示対象外の場合スキップする
		$i++;
		next if ($i < $p + 1);
		last if ($i > $p + $menu1);
	};
	my $readLog = sub {
		# ログを読み取り、各項目を変数に代入してリストで返す
		chomp($_);
		($num,$sub,$res,$nam,$date,$na2,$key,$upl,$ressub,$restime) = split(/<>/);
		$sub =~ s/\0*//g; # 文字化け対策として、タイトルに含まれているnull文字(\0)を削除
		$orig_sub = $sub; # スレッドタイトルを別途保管
	};
	my $judgeCategory = sub {
		next if $sub !~ /$in{'k'}$/; # タイトル末尾にカテゴリ名を含まない場合はスキップする
	};
	open(IN,"$nowfile") || &error("Open Error: $nowfile");
	$top = <IN>;
	while (<IN>) {
		local ($num,$sub,$res,$nam,$date,$na2,$key,$upl,$ressub,$restime,$orig_sub);

		# ログ読み取り処理実行
		if ($in{'k'} eq '') {
			# カテゴリ表示機能 無効時
			$countLog->();
			$readLog->();
		} else {
			# カテゴリ表示機能 有効時
			$readLog->();
			$judgeCategory->();
			$countLog->();
		}

		# NGスレッド一致判定
		my $is_ngthread = 0;
		if ($ngthread->is_ng_thread_creator($nam) || $ngthread->is_ng_thread_title($orig_sub)) {
			# 一致する場合
			if ($ngthread_display_mode == NGThread::DisplayMode_Hide) {
				# スレッド非表示の場合はスキップ
				next;
			} else {
				# スレッド名置換の場合は置き換える
				$is_ngthread = 1;
			}
		}

		if ($key eq '0' || $key == 4) { $icon = 'fold3.gif';$test = 'test1';$test_td = 'test1_td';$locked = '【ロック中】'; }
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
	# 残りの表示範囲外のスレッド件数カウント
	if ($in{'k'} eq '') {
		# カテゴリ表示機能無効時はバッファに一斉に読み込み改行をカウント
		local $/ = undef;
		my $buffer = <IN>;
		$i += ($buffer =~ tr/\n//);
	} else {
		# 有効時は1行ずつタイトル末尾が一致するか確認してカウント
		while(<IN>) {
			chomp($_);
			(my $sub = (split(/<>/))[1]) =~ s/\0*//g;
			$i++ if $sub =~ /$in{'k'}$/;
		}
	}
	close(IN);

	print "</table></Td></Tr></Table>\n";


	# ページ移動ボタン表示
	if ($p - $menu1 >= 0 || $p + $menu1 < $i) {
		print "<br><br><table>\n";

		# 現在表示ページ/全ページ数表示
		my $pages = int(($i - 1) / $menu1) + 1; # 全ページ数取得
		if ($p < 0) {
			# マイナスが指定された時は、1ページ目とする
			$p = 0;
		} elsif ($p + 1 > $i) {
			# 全スレッド件数より大きい値が指定された時は、最終ページ指定とする
			$p = ($pages - 1) * $menu1;
		}
		my $current_page = int($p / $menu1) + 1; # 現在表示ページ取得
		print "<tr><td class=\"num\" align=\"center\">$current_page/$pages</td></tr>\n";

		# 1ページ目・前後ページ・最終ページへのリンク
		my $k_html = exists($in{k}) ? "k=$in{k}&" : '';
		print "<tr><td class=\"num\">";
		if ($current_page <= 1) {
			print "&lt;&lt;　前へ　";
		} else {
			my $prev_page = ($current_page - 2) * $menu1;
			print "<a href=\"$bbscgi?${k_html}p=0\">&lt;&lt;</a>　<a href=\"$bbscgi?${k_html}p=$prev_page\">前へ</a>　";
		}
		if ($current_page >= $pages) {
			print "次へ　&gt;&gt;";
		} else {
			my $next_page = $current_page * $menu1;
			my $last_page = ($pages - 1) * $menu1;
			print "<a href=\"$bbscgi?${k_html}p=$next_page\">次へ</a>　<a href=\"$bbscgi?${k_html}p=$last_page\">&gt;&gt;</a>";
		}
		print "</td></tr>\n";

		print "</table>\n";
	}

	# 著作権表示（削除不可）

	# NGスレッド表示モード取得
	my $ngthread_display_mode_text = do {
		if ($ngthread_display_mode == NGThread::DisplayMode_Hide) {
			'スレッドを非表示';
		} else {
			'スレッド名を置換';
		}
	};
	# スレッド作成者のNG設定を取得
	my $ngthread_ng_thread_creator = $ngthread->get_ng_thread_creator();
	# スレッド名のNG設定を取得
	my $ngthread_ng_thread_title = $ngthread->get_ng_thread_title();
	# スレッド名のNGの除外設定を取得
	my $ngthread_ng_thread_title_exclude = $ngthread->get_ng_thread_title_exclude();
	print <<"EOM";
<br><br>



<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2"><td bgcolor="$col2" align="center">
<img src="$imgurl/foldnew.gif"> 新しい書き込みのあるスレッド &nbsp;&nbsp;
<img src="$imgurl/fold1.gif" alt="標準スレッド"> 標準スレッド &nbsp;&nbsp;
<img src="$imgurl/fold6.gif" alt="添付あり"> 添付あり &nbsp;&nbsp;
<img src="$imgurl/fold3.gif" alt="ロック中"> ロック中（書込不可）&nbsp;&nbsp;
<img src="$imgurl/fold5.gif" alt="アラーム"> アラーム（返信数$alarm件以上）&nbsp;&nbsp;
<img src="$imgurl/faq.gif"> ＦＡＱスレッド&nbsp;&nbsp;
<img src="$imgurl/look.gif" alt="管理者メッセージ"> 管理者メッセージ
</td></tr></table></Td></Tr></Table><br><br>
<!-- 著作権表\示部・削除禁止 ($ver) -->
<span class="s1">
- <a href="http://www.kent-web.com/" target="_top">Web Patio</a> -
 <a href="http://kirishima.it/patio/" target="_top">きりしま式</a> -
</span></div>
</body>
</html>
EOM
	exit;
}

#-------------------------------------------------
#  URLエンコード
#-------------------------------------------------
sub url_enc {
	local($_) = @_;

	s/(\W)/'%' . unpack('H2', $1)/eg;
	s/\s/+/g;
	$_;
}

#-------------------------------------------------
#  ログオフ
#-------------------------------------------------
sub logoff {
	if ($my_ckid =~ /^\w+$/) {
		unlink("$sesdir/$my_ckid.cgi");
	}
	print "Set-Cookie: patio_member=;\n";

	&enter_disp;
}

#-------------------------------------------------
#  RSS(2.0)フィード
#-------------------------------------------------
sub rssfeed {

	if ($in{'no'} ne "") {

		# スレッド読み込み
		open(IN,"$logdir/$in{'no'}.cgi") || &error("Open Error: $logdir/$in{'no'}.cgi");
		eval "flock(IN, 1);";
		my $top = <IN>;

		# ファイルポインタ記憶
		my $toptell = tell(IN);

		# 親記事からRSSヘッダ生成
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

		# ポインタ復元
		seek(IN,$toptell,0);

		# 新着順で表示
		my $i = 0;
		my @art = <IN>;
		@art = reverse(@art);

		foreach (@art) {
			$i++; last if ($t_max < $i);
			chomp;
			my($no2,$sub,$nam,$com,$tim) = (split(/<>/))[0,1,2,4,11];

			# 投稿日時を整形
			my @ltime = split(/\s+/,localtime($tim));
			my $rsstime = "$ltime[0], $ltime[2] $ltime[1] $ltime[4] $ltime[3] +0900";

			# 実体参照無効化
			$com =~ s/&/&amp;/g;

			# 改行をサニタイジング・BBCode削除
			$com =~ s/<br>/&lt;br \/&gt;/g;
			$com =~ s/\[b\](.*?)\[\/b\]/$1/ig;
			$com =~ s/\[i\](.*?)\[\/i\]/$1/ig;
			$com =~ s/\[u\](.*?)\[\/u\]/$1/ig;
			$com =~ s/\[s\](.*?)\[\/s\]/$1/ig;
			$com =~ s/\[code\](.*?)\[\/code\]/$1/ig;
			$com =~ s/\[url=((?:htt|ft)ps?\:[\w\.\~\-\/\?\&\+\=\:\@\%\;\#\%\,]+)\](.*?)\[\/url\]/$1/ig;
			$com =~ s/\[color=(\#[0-9A-F]{6}|[A-Z]+)\](.*?)\[\/color\]/$2/ig;

			# 親記事の場合は番号を指定しない
			my $resnum = ''; $resnum = "&amp;l=$no2" if ($no2 != 0);

			# アイテム表示
			print "<item>\n";
			print "<title>$sub ( $no2 ) by $nam</title>\n";
			print "<link>$rss_readcgi?no=$in{'no'}$resnum</link>\n";
			print "<description>&lt;p&gt;$com&lt;/p&gt;</description>\n";
			print "<pubDate>$rsstime</pubDate>\n";
			print "</item>\n\n";
		}

		close(IN);

	} else {

		# index読み込み
		open(IN,"$nowfile") || &error("Open Error: $nowfile");
		eval "flock(IN, 1);";

		print "Content-type: text/xml\n\n";

		# RSSヘッダ
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
			#スレッドタイトルが設定値に中間一致で合致するスレッドは、RSS（patio.cgi?mode=feedの一覧）に出力しません。
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

			# 実体参照無効化
			$ressub =~ s/&/&amp;/g;
			$na2 =~ s/&/&amp;/g;

			# 投稿日時を整形
			my @ltime = split(/\s+/,localtime($restime));
			my $rsstime = "$ltime[0], $ltime[2] $ltime[1] $ltime[4] $ltime[3] +0900";

			# アイテム表示
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
#  NGスレッド表示設定
#-------------------------------------------------
sub set_ngthread_display_mode {
	my $value = int($in{'display_mode'});

	# 入力値チェック
	if ($value != NGThread::DisplayMode_Hide && $value != NGThread::DisplayMode_Replace) {
		error("不正な値です");
	}

	# 書込IDログ/Cookie保存
	my $ngthread = do {
		if (defined(my $chistory_id = HistoryCookie->new()->get_history_id())) {
			# 書込IDログイン済みの場合、書込IDログを使用するよう初期化
			NGThread->new(HistoryLog->new($chistory_id));
		} else {
			# それ以外の場合は、Cookieを使用するよう初期化
			NGThread->new();
		}
	};
	$ngthread->set_display_mode($value);
	$ngthread->save();
	$ngthread->DESTROY();

	# 完了画面表示
	if ($value == NGThread::DisplayMode_Hide) {
		success('「スレッドを非表示」に設定しました。', $bbscgi);
	} else {
		success('「スレッド名を置換」に設定しました。', $bbscgi);
	}
	exit;
}

#-------------------------------------------------
#  NGスレッドワード設定
#-------------------------------------------------
sub set_ngthread_words {
	# 値をセット
	my $ngthread = do {
		if (defined(my $chistory_id = HistoryCookie->new()->get_history_id())) {
			# 書込IDログイン済みの場合、書込IDログを使用するよう初期化
			NGThread->new(HistoryLog->new($chistory_id));
		} else {
			# それ以外の場合は、Cookieを使用するよう初期化
			NGThread->new();
		}
	};
	$ngthread->set_ng_thread_creator($in{'ng_thread_creator'});             # スレッド作成者のNG設定
	$ngthread->set_ng_thread_title($in{'ng_thread_title'});                 # スレッド名のNG設定
	$ngthread->set_ng_thread_title_exclude($in{'ng_thread_title_exclude'}); # スレッド名のNGの除外設定

	# Cookie保存
	$ngthread->save();

	# NGThread HistoryLogインスタンス解放
	$ngthread->DESTROY();

	# 完了画面表示
	success('NGスレッドワードに設定しました。', $bbscgi);
	exit;
}
