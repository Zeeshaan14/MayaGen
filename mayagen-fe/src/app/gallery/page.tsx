'use client';

import { useState, useEffect } from 'react';
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, Search, Filter, Grid, LayoutGrid, Image as ImageIcon, User, Calendar, Sparkles, FolderOpen } from "lucide-react";
import Link from 'next/link';
import { toast } from "sonner";

interface GalleryImage {
  id: number;
  url: string;
  filename: string;
  category: string;
  created_by: string;
  status: string;
  prompt: string;
  model: string;
  created_at: string;
}

const MODEL_NAMES: Record<string, string> = {
  sd15: "DreamShaper 8",
  lcm: "SD 1.5 Base",
  flux: "Flux",
};

export default function GalleryPage() {
  const { user } = useAuth();
  const [gallery, setGallery] = useState<GalleryImage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [modelFilter, setModelFilter] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'masonry'>('masonry');

  // Extract unique categories
  const categories = [...new Set(gallery.map(img => img.category))];

  // Filtered gallery
  const filteredGallery = gallery.filter(img => {
    const matchesSearch = img.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          img.filename.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || img.category === categoryFilter;
    const matchesModel = modelFilter === 'all' || img.model === modelFilter;
    return matchesSearch && matchesCategory && matchesModel;
  });

  const fetchGallery = async () => {
    setIsLoading(true);
    try {
      const res = await api.get('/images');
      if (res.data.success) {
        setGallery(res.data.data.images);
      }
    } catch (e) {
      console.error("Failed to fetch gallery", e);
      toast.error("Failed to load gallery");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchGallery();
  }, []);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 pb-24">
      {/* Header */}
      <header className="sticky top-0 z-40 backdrop-blur-lg bg-neutral-950/80 border-b border-neutral-800">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ImageIcon className="w-6 h-6 text-indigo-400" />
              <h1 className="text-xl font-bold">Gallery</h1>
              <Badge variant="secondary" className="bg-neutral-800 text-neutral-300">
                {filteredGallery.length} images
              </Badge>
            </div>
            
            <Link href="/">
              <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700">
                <Sparkles className="w-4 h-4 mr-2" />
                Generate New
              </Button>
            </Link>
          </div>

          {/* Filters Row */}
          <div className="flex flex-wrap items-center gap-3 mt-4">
            {/* Search */}
            <div className="relative flex-1 min-w-[200px] max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
              <Input
                placeholder="Search prompts..."
                className="pl-9 bg-neutral-900 border-neutral-800 focus:border-indigo-500"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Category Filter */}
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-[160px] bg-neutral-900 border-neutral-800">
                <FolderOpen className="w-4 h-4 mr-2 text-neutral-500" />
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent className="bg-neutral-900 border-neutral-700">
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map(cat => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Model Filter */}
            <Select value={modelFilter} onValueChange={setModelFilter}>
              <SelectTrigger className="w-[160px] bg-neutral-900 border-neutral-800">
                <Filter className="w-4 h-4 mr-2 text-neutral-500" />
                <SelectValue placeholder="Model" />
              </SelectTrigger>
              <SelectContent className="bg-neutral-900 border-neutral-700">
                <SelectItem value="all">All Models</SelectItem>
                <SelectItem value="sd15">DreamShaper 8</SelectItem>
                <SelectItem value="lcm">SD 1.5 Base</SelectItem>
                <SelectItem value="flux">Flux</SelectItem>
              </SelectContent>
            </Select>

            {/* View Toggle */}
            <div className="flex items-center gap-1 bg-neutral-900 rounded-lg p-1 border border-neutral-800">
              <Button
                variant="ghost"
                size="icon"
                className={`h-8 w-8 ${viewMode === 'masonry' ? 'bg-neutral-800' : ''}`}
                onClick={() => setViewMode('masonry')}
              >
                <LayoutGrid className="w-4 h-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className={`h-8 w-8 ${viewMode === 'grid' ? 'bg-neutral-800' : ''}`}
                onClick={() => setViewMode('grid')}
              >
                <Grid className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Gallery Grid */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="aspect-square rounded-xl bg-neutral-900 animate-pulse" />
            ))}
          </div>
        ) : filteredGallery.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-[50vh] text-neutral-500">
            <ImageIcon className="w-16 h-16 mb-4 opacity-20" />
            <p className="text-lg mb-2">No images found</p>
            <p className="text-sm opacity-50">
              {searchQuery || categoryFilter !== 'all' || modelFilter !== 'all'
                ? "Try adjusting your filters"
                : "Start generating to see your creations here"}
            </p>
          </div>
        ) : viewMode === 'masonry' ? (
          // Masonry Layout
          <div className="columns-2 md:columns-3 lg:columns-4 gap-4 space-y-4">
            {filteredGallery.map((img) => (
              <GalleryCard key={img.id} image={img} />
            ))}
          </div>
        ) : (
          // Grid Layout
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {filteredGallery.map((img) => (
              <GalleryCard key={img.id} image={img} isSquare />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function GalleryCard({ image, isSquare }: { image: GalleryImage; isSquare?: boolean }) {
  // Case-insensitive status check
  const status = image.status?.toUpperCase();
  const isProcessing = status === 'PENDING' || status === 'PROCESSING';
  const isFailed = status === 'FAILED';
  const isCompleted = status === 'COMPLETED';

  return (
    <Link
      href={`/image/${image.id}`}
      className={`relative group rounded-xl overflow-hidden bg-neutral-900 border border-neutral-800 hover:border-indigo-500/50 transition-all duration-300 block ${isSquare ? '' : 'break-inside-avoid mb-4'}`}
    >
      {isProcessing ? (
        /* Beautiful Skeleton Loading */
        <div className={`${isSquare ? 'aspect-square' : 'aspect-[3/4]'} relative overflow-hidden`}>
          {/* Animated gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-neutral-900 via-neutral-800 to-neutral-900" />
          
          {/* Shimmer effect */}
          <div className="absolute inset-0 -translate-x-full animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/5 to-transparent" />
          
          {/* Content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 p-4">
            <div className="relative">
              <div className="w-16 h-16 rounded-full bg-indigo-500/10 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
              </div>
              <div className="absolute inset-0 rounded-full border-2 border-indigo-500/30 animate-ping" />
            </div>
            <div className="text-center">
              <span className="text-xs font-semibold text-indigo-400 uppercase tracking-widest">Generating</span>
              <p className="text-[10px] text-neutral-500 mt-1 line-clamp-2 max-w-[120px]">{image.prompt?.slice(0, 50)}...</p>
            </div>
          </div>
        </div>
      ) : !isCompleted || !image.url ? (
        /* Failed or No URL state */
        <div className={`${isSquare ? 'aspect-square' : 'aspect-[3/4]'} bg-neutral-900 flex flex-col items-center justify-center gap-2`}>
          <ImageIcon className="w-10 h-10 text-neutral-700" />
          <span className="text-xs text-neutral-600">{isFailed ? 'Generation Failed' : 'Loading...'}</span>
        </div>
      ) : (
        /* Completed Image */
        <img
          src={image.url}
          alt={image.filename}
          className={`w-full ${isSquare ? 'aspect-square object-cover' : 'h-auto'} block`}
          loading="lazy"
        />
      )}

      {/* Hover Overlay - Only for completed */}
      {isCompleted && image.url && (
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col justify-end p-4">
          <p className="text-white text-sm line-clamp-2 mb-2 font-medium">{image.prompt}</p>
          <div className="flex items-center justify-between text-xs text-neutral-400">
            <Badge className="bg-white/10 text-white border-none text-xs">
              {MODEL_NAMES[image.model] || image.model}
            </Badge>
            <div className="flex items-center gap-1">
              <User className="w-3 h-3" />
              <span>{image.created_by}</span>
            </div>
          </div>
        </div>
      )}

      {/* Status Badge */}
      {!isCompleted && (
        <div className="absolute top-2 right-2">
          <Badge className={`text-xs ${
            isFailed ? 'bg-red-900/80 text-red-300' : 
            isProcessing ? 'bg-indigo-900/80 text-indigo-300 animate-pulse' : 
            'bg-yellow-900/80 text-yellow-300'
          }`}>
            {status}
          </Badge>
        </div>
      )}
    </Link>
  );
}
