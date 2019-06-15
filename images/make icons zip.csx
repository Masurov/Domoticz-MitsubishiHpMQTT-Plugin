#r "nuget:SixLabors.ImageSharp/1.0.0-beta0006"

using System.Drawing;
using System.IO.Compression;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using SixLabors.ImageSharp.Processing;

//string imagepath = @"c:\Users\Vincent\Documents\Repos\HeatPump\integrations\domoticz\images\fan.png";

string icondesc = "Icon";

foreach( string imagepath in Directory.EnumerateFiles(@"C:\Users\Vincent\Documents\Repos\HeatPump\integrations\domoticz\images\temp2\", "*.png"))
{
    string basepath = Path.GetDirectoryName(imagepath);
    
    basepath.Dump();
    
    string basename = Path.GetFileNameWithoutExtension(imagepath);
    basename.Dump();
    
    string onfile = Path.Combine(basepath, basename + "48_On.png");
    string offfile = Path.Combine(basepath, basename + "48_Off.png"); 
    string smallfile = Path.Combine(basepath, basename + ".png");
    string txtfile = Path.Combine(basepath, "icons.txt");
    
    File.Copy(imagepath, onfile);
    File.Copy(imagepath, offfile);
    
    using (Image<Rgba32> image = Image.Load(onfile))
    {
        image.Mutate(x => x
             .Resize(16, 16)
             );
        image.Save(smallfile); // Automatic encoder selected based on extension.
    }
    
    string iconfilecontent = string.Format("{0};{0} {1};{0} {1}", basename, icondesc);
    File.WriteAllText(txtfile,iconfilecontent);
    
    var files = new List<string>{ 
    onfile,
    offfile,
    smallfile,
    txtfile
    };
    
    using (var fileStream = new FileStream(Path.Combine(basepath, basename + ".zip"), FileMode.CreateNew))
    {
        using (var archive = new ZipArchive(fileStream, ZipArchiveMode.Create, true))
        {
            foreach (var filepath in files)
            {
                var pdfBytes = File.ReadAllBytes(filepath);
                var fileName = Path.GetFileName(filepath);
                var zipArchiveEntry = archive.CreateEntry(fileName, CompressionLevel.Fastest);
                using (var zipStream = zipArchiveEntry.Open())
                {
                    zipStream.Write(pdfBytes, 0, pdfBytes.Length);
                }
            }
        }
        fileStream.Close();
    }
    
    foreach (var filepath in files)
    {
        File.Delete(filepath);
    }
}