Add-Type -AssemblyName System.Drawing
$outDir = 'C:/Users/Nuffi/.codex/visualizations/2026/09/22/01a0c949-3bd6-7251-bc27-31396855187b/Armed-Forces-Video'
[IO.Directory]::CreateDirectory($outDir) | Out-Null
$slides = @(
 @('ARMED FORCES','MEDLEY','','',''),
 @('U.S. MARINE','CORPS','U.S. Marine Corps','The Marine Hymn','Jaques Offenbach'),
 @('U.S. NAVY','','U.S. Navy',"Anchors A'Weigh",'Charles Zimmerman'),
 @('U.S. COAST','GUARD','U.S. Coast Guard','Semper Paratus','Capt. Francis Saltus van Boskerk'),
 @('U.S. ARMY','','U.S. Army','And the Caissons Go Rolling Along','Brig. General Edmind L. Gruber'),
 @('U.S. AIR FORCE','','Air Force','The U.S. Air Force','Robert Crawford'),
 @('ARMED FORCES','MEDLEY','','','')
)
$ivory = [Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml('#F5F1E5'))
$muted = [Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml('#B4CCCA'))
$pen = [Drawing.Pen]::new([Drawing.ColorTranslator]::FromHtml('#8CAAA7'),2)
$center = [Drawing.StringFormat]::new()
$center.Alignment = [Drawing.StringAlignment]::Center
$center.LineAlignment = [Drawing.StringAlignment]::Center
$hero = [Drawing.Font]::new('Georgia',100,[Drawing.FontStyle]::Bold,[Drawing.GraphicsUnit]::Pixel)
$small = [Drawing.Font]::new('Arial',25,[Drawing.FontStyle]::Regular,[Drawing.GraphicsUnit]::Pixel)
$credit = [Drawing.Font]::new('Arial',35,[Drawing.FontStyle]::Italic,[Drawing.GraphicsUnit]::Pixel)
$photo = [Drawing.Image]::FromFile('C:/Users/Nuffi/AppData/Local/Temp/codex-clipboard-805c3b1f-cb61-42aa-add8-f1202e4ef5a7.png')
for($i=0; $i -lt $slides.Count; $i++) {
 $s = $slides[$i]
 $bmp = [Drawing.Bitmap]::new(1920,1080)
 $g = [Drawing.Graphics]::FromImage($bmp)
 $g.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
 $g.TextRenderingHint = [Drawing.Text.TextRenderingHint]::AntiAliasGridFit
 $bg = [Drawing.Drawing2D.LinearGradientBrush]::new([Drawing.Point]::new(0,0),[Drawing.Point]::new(1920,1080),[Drawing.ColorTranslator]::FromHtml('#004C54'),[Drawing.ColorTranslator]::FromHtml('#06282D'))
 $g.FillRectangle($bg,0,0,1920,1080)
 $g.DrawRectangle($pen,45,45,1830,990)
 $g.DrawString('HONORING THOSE WHO SERVED',$small,$muted,[Drawing.RectangleF]::new(100,105,1720,50),$center)
 $army = $i -eq 4
 $cx = 960
 if($army){$cx=650}
 # Simple five-point star, drawn as a vector ornament.
 $points = [Drawing.PointF[]]::new(10)
 for($j=0;$j -lt 10;$j++) {
  $r=42; if($j%2 -eq 1){$r=18}
  $a=-[Math]::PI/2+$j*[Math]::PI/5
  $points[$j]=[Drawing.PointF]::new($cx+$r*[Math]::Cos($a),270+$r*[Math]::Sin($a))
 }
 $g.FillPolygon($muted,$points)
 $left=100; $width=1720
 if($army){$width=1100}
 if($s[1]) {
  $g.DrawString($s[0],$hero,$ivory,[Drawing.RectangleF]::new($left,360,$width,135),$center)
  $g.DrawString($s[1],$hero,$ivory,[Drawing.RectangleF]::new($left,495,$width,135),$center)
 } else {
  $g.DrawString($s[0],$hero,$ivory,[Drawing.RectangleF]::new($left,400,$width,180),$center)
 }
 if($army) {
  $g.InterpolationMode=[Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g.DrawImage($photo,1320,230,420,495)
  $g.DrawRectangle($pen,1320,230,420,495)
  $g.DrawString('Howard Clay Hackman',$credit,$ivory,[Drawing.RectangleF]::new(1250,740,560,55),$center)
 }
 $g.DrawLine($pen,150,835,1770,835)
 if($s[2]) {
  $fontSize=43
  do {
   $bold=[Drawing.Font]::new('Arial',$fontSize,[Drawing.FontStyle]::Bold,[Drawing.GraphicsUnit]::Pixel)
   $italic=[Drawing.Font]::new('Arial',$fontSize,[Drawing.FontStyle]::Italic,[Drawing.GraphicsUnit]::Pixel)
   $first=$s[2]+' - '
   $w1=$g.MeasureString($first,$bold).Width
   $w2=$g.MeasureString($s[3],$italic).Width
   if($w1+$w2 -le 1620){break}
   $bold.Dispose();$italic.Dispose();$fontSize-=1
  } while($fontSize -gt 25)
  $x=(1920-$w1-$w2)/2
  $g.DrawString($first,$bold,$ivory,[single]$x,[single]877)
  $g.DrawString($s[3],$italic,$ivory,[single]($x+$w1),[single]877)
  $g.DrawString($s[4],$credit,$muted,[Drawing.RectangleF]::new(100,945,1720,55),$center)
  $bold.Dispose();$italic.Dispose()
 } else {
  $g.DrawString('Armed Forces Medley',$credit,$ivory,[Drawing.RectangleF]::new(100,880,1720,60),$center)
  $g.DrawString('The Vocal Majority',$credit,$muted,[Drawing.RectangleF]::new(100,945,1720,55),$center)
 }
 $bmp.Save((Join-Path $outDir ('slide-'+$i+'.png')),[Drawing.Imaging.ImageFormat]::Png)
 $g.Dispose();$bmp.Dispose();$bg.Dispose()
}
$photo.Dispose()
Write-Output $outDir
