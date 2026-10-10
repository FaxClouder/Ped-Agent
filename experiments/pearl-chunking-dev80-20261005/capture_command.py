"""Execute one local command and exclusively save its return code and full logs."""
import argparse
import subprocess
from pathlib import Path
from runtime import save_json

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args();command=a.command[1:] if a.command[:1]==['--'] else a.command
    if not command:p.error('command required after --')
    out=a.receipt.with_suffix('.stdout.log');err=a.receipt.with_suffix('.stderr.log')
    if any(x.exists() for x in (a.receipt,out,err)):raise FileExistsError('new receipt and log names required')
    with out.open('x',encoding='utf8') as stdout,err.open('x',encoding='utf8') as stderr:
        result=subprocess.run(command,stdout=stdout,stderr=stderr)
    save_json(a.receipt,{'argv':command,'exit_code':result.returncode,'stdout':out.name,'stderr':err.name})
    print('saved',a.receipt,'exit_code',result.returncode,flush=True)
    raise SystemExit(result.returncode)

if __name__=='__main__':main()
