#!/usr/bin/env python3
"""Stage manifest-listed Pages files; verified R2 assets retain their same public URLs."""
import argparse, concurrent.futures, hashlib, json, shutil, subprocess
from pathlib import Path
from verify_public_release import verify

def stage(root, destination, media_map):
    root=Path(root).resolve();destination=Path(destination).absolute()
    if destination.exists(): raise ValueError('Destination must not exist')
    verify(root)
    manifest=json.loads((root/'release-manifest.json').read_text())
    media=json.loads(Path(media_map).read_text())
    if len(media)!=311: raise ValueError('Unexpected reviewed media inventory')
    for url,e in media.items():
        if not url.startswith('/') or url.startswith('//') or '?' in url or '#' in url or '..' in Path(url).parts: raise ValueError('Unsafe media path')
        if manifest['files'].get(url[1:])!=e['sha256']: raise ValueError('Media differs from accepted artifact')
        if (root/url[1:]).stat().st_size!=e['bytes']: raise ValueError('Media length differs')
    def live(item):
        url,e=item
        r=subprocess.run(['curl','--fail','--silent','--show-error','--retry','2','--max-time','40','--head','--header','Accept-Encoding: identity','https://chappaquapoison.com'+url],capture_output=True,text=True)
        h={k.lower():v.strip() for line in r.stdout.splitlines() if ': ' in line for k,v in [line.split(': ',1)]}
        if r.returncode or h.get('etag')!='"sha256-'+e['sha256']+'"' or h.get('content-length')!=str(e['bytes']) or h.get('content-type','').split(';')[0]!=e['mime']: raise ValueError('Live media unavailable or changed: '+url)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(live,media.items()))
    destination.mkdir(parents=True)
    try:
        size=0;count=0
        for name,expected in manifest['files'].items():
            if '/'+name in media: continue
            data=(root/name).read_bytes()
            if hashlib.sha256(data).hexdigest()!=expected:raise ValueError('Source changed while staging: '+name)
            target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);size+=len(data);count+=1
        if size>=1024**3:raise ValueError('Pages package exceeds 1 GiB')
        public=dict(manifest);public['delivery']={'pages_file_count':count,'pages_content_bytes':size,'media_worker_paths':media}
        (destination/'release-manifest.json').write_text(json.dumps(public,indent=2)+'\n')
        (destination/'.nojekyll').write_text('')
        print(json.dumps({'build_id':manifest['build_id'],'pages_files':count,'pages_content_bytes':size,'verified_live_media':len(media)}))
    except Exception:
        # Do not leave a publication manifest on an incomplete staging directory.
        (destination/'release-manifest.json').unlink(missing_ok=True)
        raise
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--destination',required=True);p.add_argument('--media-map',required=True);a=p.parse_args();stage(a.root,a.destination,a.media_map)
