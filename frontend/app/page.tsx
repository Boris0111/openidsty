import {Explorer} from '@/components/Explorer';
import {Suspense} from 'react';
import {Status} from '@/components/Status';
export default function Home(){return <Suspense fallback={<Status loading/>}><Explorer/></Suspense>}
