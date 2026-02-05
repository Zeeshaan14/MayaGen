'use client';

import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function ImageDetailPage() {
  const params = useParams();

  return (
    <div className="p-10 text-white">
      <h1>Debug View: Image {params.id}</h1>
      <Link href="/">
        <Button>Back Home</Button>
      </Link>
    </div>
  );
}
