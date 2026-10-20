import {NextRequest} from 'next/server';
import {proxySession} from '@/lib/admin-proxy';
export const dynamic='force-dynamic';
export const runtime='nodejs';
export function GET(request:NextRequest){return proxySession(request)}
export function POST(request:NextRequest){return proxySession(request)}
export function DELETE(request:NextRequest){return proxySession(request)}
