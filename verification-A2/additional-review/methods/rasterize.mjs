import sharp from 'sharp';
import {writeFile} from 'node:fs/promises';
const suffix=process.env.AUDIT_LABEL==='A2'?'-original':'';
for(const side of ['top','inner_1','inner_2','bottom']){
 const data=await sharp(`work/independent-audit/gerber-raster${suffix}/${side}.svg`,{density:1270,limitInputPixels:false}).resize(5000,5000).removeAlpha().greyscale().raw().toBuffer();
 await writeFile(`work/independent-audit/gerber-raster${suffix}/${side}.raw`,data);
 console.log(side,'5000 x 5000',data.length);
}
