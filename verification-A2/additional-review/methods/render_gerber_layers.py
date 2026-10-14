from pathlib import Path
import json,warnings,os
from gerbonara.layers import LayerStack
from gerbonara.utils import MM
label=os.environ.get('AUDIT_LABEL','A2-Economy');out=Path('work/independent-audit/gerber-raster'+('-original' if label=='A2' else ''));out.mkdir(exist_ok=True)
with warnings.catch_warnings(record=True) as ws:
 warnings.simplefilter('always');b=LayerStack.open('outputs/revision-'+label+'/Two-computer-switch-'+label+'-Gerbers.zip')
 for side in ['top','inner_1','inner_2','bottom']:
  (out/(side+'.svg')).write_text(str(b.graphic_layers[side,'copper'].to_svg(force_bounds=((0,-100),(100,0)),fg='white',bg='black')))
 holes=[]
 for o in b.drill_pth.objects:
  bb=o.bounding_box(MM);holes.append({'xy':[(bb[0][0]+bb[1][0])/2,-(bb[0][1]+bb[1][1])/2],'bounds':bb})
 (out/'drills.json').write_text(json.dumps(holes));(out/'parser-warnings.json').write_text(json.dumps([str(w.message).split(': ',1)[-1] for w in ws],indent=2))
 print('Copper layers rendered; plated drill objects',len(holes))
