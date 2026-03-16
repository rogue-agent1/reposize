#!/usr/bin/env python3
"""reposize - Analyze local git repo size breakdown."""
import subprocess, os, argparse, sys, collections

def fmt(b):
    for u in ['B','KB','MB','GB']:
        if b < 1024: return f"{b:.1f}{u}"
        b /= 1024
    return f"{b:.1f}TB"

def main():
    p = argparse.ArgumentParser(description='Git repo size analyzer')
    p.add_argument('path', nargs='?', default='.')
    p.add_argument('-n', '--top', type=int, default=20)
    p.add_argument('--git', action='store_true', help='Include .git directory')
    args = p.parse_args()

    # Tracked files by extension
    tracked = subprocess.check_output(['git', 'ls-files'], text=True, cwd=args.path).strip().split('\n')
    
    ext_size = collections.Counter()
    ext_count = collections.Counter()
    large_files = []
    total = 0
    
    for f in tracked:
        if not f: continue
        fp = os.path.join(args.path, f)
        try:
            size = os.path.getsize(fp)
        except OSError:
            continue
        ext = f.rsplit('.', 1)[-1].lower() if '.' in f else '(none)'
        ext_size[ext] += size
        ext_count[ext] += 1
        total += size
        large_files.append((size, f))
    
    large_files.sort(reverse=True)
    
    # .git size
    git_dir = os.path.join(args.path, '.git')
    git_size = 0
    if os.path.isdir(git_dir):
        for root, dirs, files in os.walk(git_dir):
            for f in files:
                try: git_size += os.path.getsize(os.path.join(root, f))
                except: pass
    
    print(f"Repository: {os.path.abspath(args.path)}")
    print(f"Tracked files: {len(tracked)}")
    print(f"Working tree:  {fmt(total)}")
    print(f".git directory: {fmt(git_size)}")
    print(f"Total:          {fmt(total + git_size)}")
    
    print(f"\nBy extension:")
    for ext, size in ext_size.most_common(15):
        count = ext_count[ext]
        pct = size / total * 100 if total else 0
        bar = '█' * int(pct / 3)
        print(f"  .{ext:<10} {fmt(size):>8}  {count:>5} files  {pct:>5.1f}%  {bar}")
    
    print(f"\nLargest files:")
    for size, f in large_files[:args.top]:
        print(f"  {fmt(size):>8}  {f}")

if __name__ == '__main__':
    main()
