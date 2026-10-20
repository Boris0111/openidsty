import {redirect} from 'next/navigation';
// Theme follows now live in the shared device watchlist; the v1 storage key stays untouched as a migration backup.
export default function Page(){redirect('/next?view=watchlist')}
