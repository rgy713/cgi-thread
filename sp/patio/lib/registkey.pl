#������������������������������������������������������������
#�� �����e�L�[�p���s���W���[��
#�� registkey.pl - 2006/09/15
#�� Copyright (c) KentWeb
#�� webmaster@kent-web.com
#�� http://www.kent-web.com/
#������������������������������������������������������������

#-------------------------------------------------
#  ���e�L�[
#-------------------------------------------------
sub pcp_makekey {
	local($str_plain, $str_crypt, @number);

	# �C�ӂ̐����S�����𐶐�
	@number = (0 .. 9);
	srand;
	foreach (1 .. 4) {
		$str_plain .= $number[int(rand(@number))];
	}

	# ���Ԃ�t��
	$str_plain .= time;

	# �Í���
	$str_crypt = &pcp_encode($str_plain, $pcp_passwd);
	$str_crypt =~ s/\!/%21/g;

	return ($str_plain, $str_crypt);
}

#-------------------------------------------------
#  ���e�L�[�`�F�b�N
#-------------------------------------------------
sub registkey_chk {
	local($input, $crypt) = @_;
	local($plain, $code, $time);

	# ���e�L�[�𕜍�
	$crypt =~ s/\%21/!/g;
	$plain = &pcp_decode($crypt, $pcp_passwd);

	# �L�[�Ǝ��Ԃɕ���
	$plain =~ /^(\d{4})(\d+)/;
	$code = $1;
	$time = $2;

	# �L�[��v
	if ($input eq $code) {
		# �������ԃI�[�o�[
		if (time - $time > $pcp_time*60) {
			return 0;

		# ��������OK
		} else {
			return 1;
		}
	# �L�[�s��v
	} else {
		return -1;
	}
}

#-------------------------------------------------
#  �ȈՈÍ�
#-------------------------------------------------
#  �䂢����̈Í����T�u���[�`���𗬗p���܂���
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

