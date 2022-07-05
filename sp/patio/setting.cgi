#!/usr/bin/perl

# 設定内容表示スクリプト（なくても掲示板の動作には関係ありません）

#┌─────────────────────────────────
#│ [ WebPatio ]
#│ setting.cgi - 2006/10/09
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

# きりしま式 K0.973
# 2010/06/23 新規スレッド作成とレスのタイマーを分けてみました
# 0.74 2008/08/29 いったん一式アーカイブを更新

# 外部ファイル取り込み
require './init.cgi';
require $jcode;

$title = $title."の設定内容";

#-------------------------------------------------
#  メニュー部表示
#-------------------------------------------------


	$hothour = int ($hot/3600);
	
	&header();
	print <<"EOM";
<div align="center">
<table width="95%"><tr><td align=right nowrap>
<a href="./patio.cgi">トップページ</a> &gt; <a href="./note.html">留意事項</a> &gt; 設定内容
</td></tr></table>
<Table border=0 cellspacing=0 cellpadding=0 width="95%">
<Tr bgcolor="#8080C0"><Td bgcolor="#8080C0">
<table border=0 cellspacing=1 cellpadding=5 width="100%">
<tr bgcolor="#DCDCED"><td bgcolor="#DCDCED" nowrap width="92%">
<img src="./img/book.gif" align="absmiddle">
&nbsp; <b>設定内容</b> $ver</td>
</tr></table></Td></Tr></Table>
<p>
<Table border="0" cellspacing="0" cellpadding="0" width="95%">
<Tr><Td bgcolor="$col1">
<table border="0" cellspacing="1" cellpadding="5" width="100%">
<tr bgcolor="$col2">
  <td bgcolor="$col1" colspan="3">
	<font color="$col2"><b>この掲示板の設定内容</b></font>
  </td>
</tr>
<tr bgcolor="$col2">
  <td bgcolor="$col2" nowrap><b>項目</b></td>
  <td bgcolor="$col2" nowrap><b>設定値</b></td>
  <td bgcolor="$col2" nowrap><b>備考</b></td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >1スレッドあたりの最大記事数</td>
  <td bgcolor="$col2" nowrap>$m_maxコメント</td>
  <td bgcolor="$col2" nowrap>レス数がこれを越えると過去ログに移行します</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >現行ログのスレッド数</td>
  <td bgcolor="$col2" nowrap>$i_maxスレッド</td>
  <td bgcolor="$col2" nowrap>スレッド数がこれを越えると古い順に過去ログに移行します</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >過去ログのスレッド数</td>
  <td bgcolor="$col2" nowrap>$p_maxスレッド</td>
  <td bgcolor="$col2" nowrap>過去ログのスレッド数がこれを越えるとスレッドは削除されます</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >スレッド作成間隔</td>
  <td bgcolor="$col2" nowrap>$wait_thread秒</td>
  <td bgcolor="$col2" nowrap>スレッドの作成はこの時間以上待ってから行なって下さい 0=無制限</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >レス投稿間隔</td>
  <td bgcolor="$col2" nowrap>$wait_response秒</td>
  <td bgcolor="$col2" nowrap>レスの投稿はこの時間以上待ってから行なって下さい 0=無制限</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >日本語チェック</td>
  <td bgcolor="$col2" nowrap>$jp_wd</td>
  <td bgcolor="$col2" nowrap>書き込みに日本語が含まれるか判定します 0=無効 1=有効</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >URL数制限</td>
  <td bgcolor="$col2" nowrap>$urlnum個まで</td>
  <td bgcolor="$col2" nowrap>投稿中に含めることが許可されているURLの数 0=無制限</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >コメント入力文字数</td>
  <td bgcolor="$col2" nowrap>$max_msg文字</td>
  <td bgcolor="$col2" nowrap>全角換算</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >最大投稿可能\サイズ</td>
  <td bgcolor="$col2" nowrap>$maxdataバイト</td>
  <td bgcolor="$col2" nowrap>本文と添付ファイルの合計</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >投稿キー許容時間</td>
  <td bgcolor="$col2" nowrap>$pcp_time分</td>
  <td bgcolor="$col2" nowrap>フォームを表\示させてから投稿するまでの時間制限</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >新着表\示時間</td>
  <td bgcolor="$col2" nowrap>$hothour時間</td>
  <td bgcolor="$col2" nowrap>新着表\示される時間</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >管理者によるパスワードクリア</td>
  <td bgcolor="$col2" nowrap>$clearpass</td>
  <td bgcolor="$col2" nowrap>管理者が編集した場合、ユーザーのパスワードをクリアするか 0=維持する 1=クリアする（ユーザーが編集できなくなる）</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >レスお知らせメール</td>
  <td bgcolor="$col2" nowrap>$mailnotify</td>
  <td bgcolor="$col2" nowrap>レスがあったときにメールでお知らせ 0=しない 1=スレッドを立てた人のみ 2=コメントした人も含め全員）</td>
</tr>
<tr bgcolor="$col1">
  <td bgcolor="$col2" >新規スレッド作成制限</td>
  <td bgcolor="$col2" nowrap>$createonlyadmin</td>
  <td bgcolor="$col2" nowrap> 0=誰でも作成できる 1=管理者のみ（ユーザーはスレッドを作成できない）</td>
</tr>
</table></Td></Tr></Table>
<br><br>
<!-- 著作権表\示部・削除禁止 ($ver) -->
<span class="s1">
- <a href="http://www.kent-web.com/" target="_top">Web Patio</a> -
 <a href="http://kirishima.cc/patio/" target="_top">きりしま式</a> -
</span></div>
</body>
</html>
EOM

