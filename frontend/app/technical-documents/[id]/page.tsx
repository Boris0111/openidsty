'use client';
import {use} from 'react';
import {useSearchParams} from 'next/navigation';
import {TechnicalDocumentReading} from '@/components/TechnicalDocuments';
export default function Page({params}:{params:Promise<{id:string}>}){const {id}=use(params);const search=useSearchParams();return <TechnicalDocumentReading key={id} id={id} version={search.get('version')}/>;}
