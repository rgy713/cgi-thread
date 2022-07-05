#┌─────────────────────────────
#│ ●投稿キー用実行モジュール
#│ registkey.pl - 2006/09/15
#│ Copyright (c) KentWeb
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────

#-------------------------------------------------
#  投稿キー
#-------------------------------------------------
sub pcp_makekey {
	local($str_plain, $str_crypt, @number);

	# 任意の数字４文字を生成
	@number = (0 .. 9);
	srand;
	foreach (1 .. 4) {
		$str_plain .= $number[int(rand(@number))];
	}

	# 時間を付加
	$str_plain .= time;

	# 暗号化
	$str_crypt = &pcp_encode($str_plain, $pcp_passwd);
	$str_crypt =~ s/\!/%21/g;

	return ($str_plain, $str_crypt);
}

#-------------------------------------------------
#  投稿キーチェック
#-------------------------------------------------
sub registkey_chk {
	local($input, $crypt) = @_;
	local($plain, $code, $time);

	# 投稿キーを復号
	$crypt =~ s/\%21/!/g;
	$plain = &pcp_decode($crypt, $pcp_passwd);

	# キーと時間に分解
	$plain =~ /^(\d{4})(\d+)/;
	$code = $1;
	$time = $2;

	# キー一致
	if ($input eq $code) {
		# 制限時間オーバー
		if (time - $time > $pcp_time*60) {
			return 0;

		# 制限時間OK
		} else {
			return 1;
		}
	# キー不一致
	} else {
		return -1;
	}
}

#-------------------------------------------------
#  簡易暗号
#-------------------------------------------------
#  ゆいさんの暗号化サブルーチンを流用しました
#  http://www.cup.com/yui/
sub pcp_decode {
  local($comment,$key,$i,$j,@key);
  $comment = $_[0];
  $key = $_[1];
  @key = split(//,$key);
  $i = 0;
  $j =  &pcp_make_Table($key);
  $comment=~ s/./$pcp_table{$&}/g;
  $comment =~ s/.../sprintf("%c",oct($&)^(ord($key[$i++ % @key]) +($j++ % 383)))/ges;
  $comment=~s/\0$//;
  return $comment;
}
sub pcp_encode {
  local($comment,$key,$i,$j,@key);
  $comment = $_[0];
  $key = $_[1];
  $comment .="\0" if(length($comment) % 2);
  @key = split(//,$key);
  $i = 0;
  $j =  &pcp_make_Table($key);
  $comment =~ s/./sprintf("%03o",ord($&)^(ord($key[$i++ % @key])+($j++ % 383)))/ges;
  $comment=~ s/../$pcp_table{$&}/g;
  return $comment;
}
sub pcp_make_Table{
  local(@list,$i,$j,$k,$init_j,@key,@seed);

  @seed = split(//,'q1aZ.XzS5xACs27wD6eE4d8c0!WvQfRFr9Gt3TgBVbNMnJhyKIujUmYkHiLlOoPp');
  @key = split(//,$_[0]);
  $k=@key;
  $init_j=0;
  for($i=0;$i<64;$i++){
    $j=ord($key[$i % $k]);
    $init_j +=$j;
    $list[$i]=splice(@seed,(($j+$k) % (64-$i)),1);
  }

  $k=0;
  for($i=0;$i<8;$i++){
    for($j=0;$j<8;$j++,$k++){
      $pcp_table{"$i$j"}=$list[$k];
      $pcp_table{$list[$k]}="$i$j";
    }
  }
  return ($init_j % 383);
}



1;

