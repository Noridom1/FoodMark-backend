import pyktok as pyk
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from ..database import supabase
import pandas as pd
import json

def extract_id_from_url(url: str) -> str:
    path = urlparse(url).path
    return path.rstrip('/').split('/')[-1]

def get_video_description(video_id: str) -> str:
    # read the CSV
    df = pd.read_csv("metadata.csv")

    # filter rows with matching video_id
    matched_rows = df[df["video_id"] == video_id]

    # get the latest one (last row)
    if not matched_rows.empty:
        latest_row = matched_rows.iloc[-1]
        metadata = latest_row.to_dict()
        return metadata['video_description']
    else:
        return ""

def upload_video_to_bucket(local_path: str):
    bucket = supabase.storage.from_("videobucket")
    
    # Extract just the filename
    filename = os.path.basename(local_path)

    # Check if file exists in bucket
    existing_files = bucket.list()
    if any(file["name"] == filename for file in existing_files):
        print(f"⚠️ File '{filename}' already exists in bucket. Skipping upload.")
        return None
    
    # Upload if not exists
    with open(local_path, "rb") as f:
        res = bucket.upload(filename, f)
        print("✅ Upload successful:", res)
        return res

def download_video_tiktok(url: str, save_dir: str = os.path.join('storage', 'videos', 'downloaded')):
    os.makedirs(save_dir, exist_ok=True)

    old_cwd = os.getcwd()
    try:
        os.chdir(save_dir)
        # pyk.specify_browser('chrome')

        try:
            save_result = pyk.save_tiktok(
                url,
                save_video=True,
                metadata_fn='metadata.csv',
                return_fns=True
            )
            # local_path = os.path.join(save_dir, save_result['video_fn'])
            local_path = save_result['video_fn']
            # storage_path = f"{save_result['video_fn']}"

            print("local_path:", local_path)
            # print("storage_path:", storage_path)
            # split by '_' and then remove the extension
            video_id = local_path.split('_')[-1].split('.')[0]

            description = get_video_description(video_id)

            upload_video_to_bucket(local_path)

            # os.remove(local_path)  # remove local file after upload

            public_url = supabase.storage.from_("videobucket").get_public_url(local_path)
            
            return public_url, description, None
        
        except Exception as e:
            return None, None, e

    finally:
        os.chdir(old_cwd)


def _download_video_sstik_internal(url: str, save_dir: str = os.path.join('storage', 'videos', 'downloaded')):
    """
    Download TikTok video using sstik.io service.
        url: The TikTok video URL to download.
    """

    os.makedirs(save_dir, exist_ok=True)

    cookies = {
        '__Secure-3PAPISID': 'fpdeMeMkm-8BgXFF/AKJAf2MT1fam6c56B',
        '__Secure-3PSID': 'g.a000zwi29CRrQdhunDEqBS4x27STM60tWsr8w69loqfoTKCksqA981BGSzUxGEJHJuuCJW47yQACgYKAeASARMSFQHGX2Mi8NaTEOKHXjGJfRKXKXtM5RoVAUF8yKr9RjYkP0ITNiyUMV7d1LDj0076',
        '__Secure-3PSIDTS': 'sidts-CjEB5H03P4TtkuMcWLOcBDwgVsodi9FV_vkbF7W8VhQXh9Ze4Er6P_K-UaYnqMm-zrI3EAA',
        'NID': '525=F9TP4JncIBm5shoSiN5ZvKzz8fQLhq2RG4JNnvuptumN9Oo60cewpQoBKry_hLqajuDaYyfYxeF4G2hJYV0SqYSdQcFs3Q78I6lOx6Zgb-bI9kM1woT5pUD6oxYnaOM7az_dXmd3XxxteB2ryKOthFrJXnLYhes4RDTw_a_9QobUV3KUG3GCtY0PM0SvAL7pEHB69NR_JPRNk66lTUIX0m0t4teqdYaWXCBqZyMXe5rh3BODuYB-_UTWodx-X82dBy4RSfXtyFY6UALLr_23VpRDLg2ZYzCht_grnagCv8h8rFqGp3NzKZNqzMh2Uo0FZl3hZtiHiCD4m1XZNotxyzYpwKTgLqKi5XUNm1VMvBKg4XPUrIRs3OMLARcvt30cvXiX1hD49T1kAD11lQEpRFe4NloSECQh3dUZGkOM5X_8ffzeJzgQbJUlXrqT1vgVmlasYcKjHX7bZJDEGT7wDhYb9SHzAqp1t-P_3B7y4fyEy_L91tZQCGUptXPix_lu-WiWVaRqXNJTUPzcFlwWuEMmY_wMl4HYu69LFYDOJySuGzE6usQMPUKNliPOR1dWP3oOsjCURRzCqr5TsvNrGyNupFxciOj5OZJRs2AlSeKv1JFre76gvRfQVMe-WBsw8pRc5sONk6ceuGYJIO_Sidij_QGJ26HHhGrK0GcWFGc5RrNbdBA9jrgD3xzM0xoQQqSpTud_tjha0nITYfpZjrwHv2yrI7NXBHAO-DCks-wBrSjT62BhlsvvYiuDFDzumw8JOKg88fuo20LpNyeIc30pvRukwu3ivsH8RRccrHrjEYUXaydPaMQ1Bp9qzqsSd2v3brUnkkVrQPMLis4M4M3Rd5MnrOAtNHE2wW-oDUDp3vjGeQra4h5DFcWdi0hGUHOHvN4iMfMrYNhHB9nJ8SJjp_KbqjEEPf6lRmewRDEaGPQiGHL1dUBaFEiV_HUIcC_AhRD1RgJiJvcCjuK16ma2A-Gm8rxcATe758mbnA_UdKfd1yW-Ph30PnYsMM7wvHZqYtGO94QvWAlUKdZXuRztMhXbD8shXrUm8-tMmzaKyDLawjRna3QbwhzG2-x6AWCWRbShrqZRLIS1imHwnW_XHvy5AGC27bAgEgGR0blZE9kPhxwC4o7auH2hEShVoeBPKKqPwcrCTwY_vWnj23ZNNAmHb4oCpE1eUOc3h0cgMKB1oroTiuL4G1UX2RUc5HfMrs1jLbKCN5fk8yjerem9KOOID1CdT6FlqxBl_Q',
        '__Secure-3PSIDCC': 'AKEyXzW7SNa0xwpAWApSkXoVkIeF7InHzzylvC3ByQpSiL5Lvc2oPJN-ykhrULR7Mp4_isfQtDA',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9,vi;q=0.8,en-US;q=0.7,zh-TW;q=0.6,zh;q=0.5',
        # 'content-length': '0',
        'origin': 'https://ssstik.io',
        'priority': 'u=1, i',
        'referer': 'https://ssstik.io/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'x-browser-channel': 'stable',
        'x-browser-copyright': 'Copyright 2025 Google LLC. All rights reserved.',
        'x-browser-validation': '6h3XF8YcD8syi2FF2BbuE2KllQo=',
        'x-browser-year': '2025',
        'x-client-data': 'CJa2yQEIo7bJAQipncoBCNqAywEIkqHLAQiko8sBCIWgzQEY4eLOAQ==',
        # 'cookie': '__Secure-3PAPISID=fpdeMeMkm-8BgXFF/AKJAf2MT1fam6c56B; __Secure-3PSID=g.a000zwi29CRrQdhunDEqBS4x27STM60tWsr8w69loqfoTKCksqA981BGSzUxGEJHJuuCJW47yQACgYKAeASARMSFQHGX2Mi8NaTEOKHXjGJfRKXKXtM5RoVAUF8yKr9RjYkP0ITNiyUMV7d1LDj0076; __Secure-3PSIDTS=sidts-CjEB5H03P4TtkuMcWLOcBDwgVsodi9FV_vkbF7W8VhQXh9Ze4Er6P_K-UaYnqMm-zrI3EAA; NID=525=F9TP4JncIBm5shoSiN5ZvKzz8fQLhq2RG4JNnvuptumN9Oo60cewpQoBKry_hLqajuDaYyfYxeF4G2hJYV0SqYSdQcFs3Q78I6lOx6Zgb-bI9kM1woT5pUD6oxYnaOM7az_dXmd3XxxteB2ryKOthFrJXnLYhes4RDTw_a_9QobUV3KUG3GCtY0PM0SvAL7pEHB69NR_JPRNk66lTUIX0m0t4teqdYaWXCBqZyMXe5rh3BODuYB-_UTWodx-X82dBy4RSfXtyFY6UALLr_23VpRDLg2ZYzCht_grnagCv8h8rFqGp3NzKZNqzMh2Uo0FZl3hZtiHiCD4m1XZNotxyzYpwKTgLqKi5XUNm1VMvBKg4XPUrIRs3OMLARcvt30cvXiX1hD49T1kAD11lQEpRFe4NloSECQh3dUZGkOM5X_8ffzeJzgQbJUlXrqT1vgVmlasYcKjHX7bZJDEGT7wDhYb9SHzAqp1t-P_3B7y4fyEy_L91tZQCGUptXPix_lu-WiWVaRqXNJTUPzcFlwWuEMmY_wMl4HYu69LFYDOJySuGzE6usQMPUKNliPOR1dWP3oOsjCURRzCqr5TsvNrGyNupFxciOj5OZJRs2AlSeKv1JFre76gvRfQVMe-WBsw8pRc5sONk6ceuGYJIO_Sidij_QGJ26HHhGrK0GcWFGc5RrNbdBA9jrgD3xzM0xoQQqSpTud_tjha0nITYfpZjrwHv2yrI7NXBHAO-DCks-wBrSjT62BhlsvvYiuDFDzumw8JOKg88fuo20LpNyeIc30pvRukwu3ivsH8RRccrHrjEYUXaydPaMQ1Bp9qzqsSd2v3brUnkkVrQPMLis4M4M3Rd5MnrOAtNHE2wW-oDUDp3vjGeQra4h5DFcWdi0hGUHOHvN4iMfMrYNhHB9nJ8SJjp_KbqjEEPf6lRmewRDEaGPQiGHL1dUBaFEiV_HUIcC_AhRD1RgJiJvcCjuK16ma2A-Gm8rxcATe758mbnA_UdKfd1yW-Ph30PnYsMM7wvHZqYtGO94QvWAlUKdZXuRztMhXbD8shXrUm8-tMmzaKyDLawjRna3QbwhzG2-x6AWCWRbShrqZRLIS1imHwnW_XHvy5AGC27bAgEgGR0blZE9kPhxwC4o7auH2hEShVoeBPKKqPwcrCTwY_vWnj23ZNNAmHb4oCpE1eUOc3h0cgMKB1oroTiuL4G1UX2RUc5HfMrs1jLbKCN5fk8yjerem9KOOID1CdT6FlqxBl_Q; __Secure-3PSIDCC=AKEyXzW7SNa0xwpAWApSkXoVkIeF7InHzzylvC3ByQpSiL5Lvc2oPJN-ykhrULR7Mp4_isfQtDA',
    }

    response = requests.post(
        'https://analytics.google.com/g/collect?v=2&tid=G-ZSF3D6YSLC&gtm=45je5870h2v9115464968za200zb810593590zd810593590&_p=1754830836756&gcd=13l3l3l3l1l1&npa=0&dma=0&tcfd=10000&tag_exp=101509157~103116026~103200004~103233427~104527907~104528501~104684208~104684211~104948813~105033766~105033768~105103161~105103163~105113531~105135708~105135710&cid=859323010.1754830598&ul=en-gb&sr=1536x864&uaa=x86&uab=64&uafvl=Not)A%253BBrand%3B8.0.0.0%7CChromium%3B138.0.7204.184%7CGoogle%2520Chrome%3B138.0.7204.184&uamb=0&uam=&uap=Windows&uapv=19.0.0&uaw=0&are=1&frm=0&pscdl=noapi&_eu=AEEAAAQ&_s=4&sid=1754830598&sct=1&seg=1&dl=https%3A%2F%2Fssstik.io%2F&dt=TikTok%20Downloader%20-%20Download%20TikTok%20Video%20Without%20Watermark&en=form_start&ep.form_id=_gcaptcha_pt&ep.form_name=&ep.form_destination=https%3A%2F%2Fssstik.io%2F&epn.form_length=5&ep.first_field_id=main_page_text&ep.first_field_name=id&ep.first_field_type=text&epn.first_field_position=1&_et=4548&tfd=17768',
        cookies=cookies,
        headers=headers,
    )


    cookies = {
        '__Secure-3PAPISID': 'fpdeMeMkm-8BgXFF/AKJAf2MT1fam6c56B',
        '__Secure-3PSID': 'g.a000zwi29CRrQdhunDEqBS4x27STM60tWsr8w69loqfoTKCksqA981BGSzUxGEJHJuuCJW47yQACgYKAeASARMSFQHGX2Mi8NaTEOKHXjGJfRKXKXtM5RoVAUF8yKr9RjYkP0ITNiyUMV7d1LDj0076',
        '__Secure-3PSIDTS': 'sidts-CjEB5H03P4TtkuMcWLOcBDwgVsodi9FV_vkbF7W8VhQXh9Ze4Er6P_K-UaYnqMm-zrI3EAA',
        'NID': '525=F9TP4JncIBm5shoSiN5ZvKzz8fQLhq2RG4JNnvuptumN9Oo60cewpQoBKry_hLqajuDaYyfYxeF4G2hJYV0SqYSdQcFs3Q78I6lOx6Zgb-bI9kM1woT5pUD6oxYnaOM7az_dXmd3XxxteB2ryKOthFrJXnLYhes4RDTw_a_9QobUV3KUG3GCtY0PM0SvAL7pEHB69NR_JPRNk66lTUIX0m0t4teqdYaWXCBqZyMXe5rh3BODuYB-_UTWodx-X82dBy4RSfXtyFY6UALLr_23VpRDLg2ZYzCht_grnagCv8h8rFqGp3NzKZNqzMh2Uo0FZl3hZtiHiCD4m1XZNotxyzYpwKTgLqKi5XUNm1VMvBKg4XPUrIRs3OMLARcvt30cvXiX1hD49T1kAD11lQEpRFe4NloSECQh3dUZGkOM5X_8ffzeJzgQbJUlXrqT1vgVmlasYcKjHX7bZJDEGT7wDhYb9SHzAqp1t-P_3B7y4fyEy_L91tZQCGUptXPix_lu-WiWVaRqXNJTUPzcFlwWuEMmY_wMl4HYu69LFYDOJySuGzE6usQMPUKNliPOR1dWP3oOsjCURRzCqr5TsvNrGyNupFxciOj5OZJRs2AlSeKv1JFre76gvRfQVMe-WBsw8pRc5sONk6ceuGYJIO_Sidij_QGJ26HHhGrK0GcWFGc5RrNbdBA9jrgD3xzM0xoQQqSpTud_tjha0nITYfpZjrwHv2yrI7NXBHAO-DCks-wBrSjT62BhlsvvYiuDFDzumw8JOKg88fuo20LpNyeIc30pvRukwu3ivsH8RRccrHrjEYUXaydPaMQ1Bp9qzqsSd2v3brUnkkVrQPMLis4M4M3Rd5MnrOAtNHE2wW-oDUDp3vjGeQra4h5DFcWdi0hGUHOHvN4iMfMrYNhHB9nJ8SJjp_KbqjEEPf6lRmewRDEaGPQiGHL1dUBaFEiV_HUIcC_AhRD1RgJiJvcCjuK16ma2A-Gm8rxcATe758mbnA_UdKfd1yW-Ph30PnYsMM7wvHZqYtGO94QvWAlUKdZXuRztMhXbD8shXrUm8-tMmzaKyDLawjRna3QbwhzG2-x6AWCWRbShrqZRLIS1imHwnW_XHvy5AGC27bAgEgGR0blZE9kPhxwC4o7auH2hEShVoeBPKKqPwcrCTwY_vWnj23ZNNAmHb4oCpE1eUOc3h0cgMKB1oroTiuL4G1UX2RUc5HfMrs1jLbKCN5fk8yjerem9KOOID1CdT6FlqxBl_Q',
        '__Secure-3PSIDCC': 'AKEyXzW7SNa0xwpAWApSkXoVkIeF7InHzzylvC3ByQpSiL5Lvc2oPJN-ykhrULR7Mp4_isfQtDA',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9,vi;q=0.8,en-US;q=0.7,zh-TW;q=0.6,zh;q=0.5',
        # 'content-length': '0',
        'origin': 'https://ssstik.io',
        'priority': 'u=1, i',
        'referer': 'https://ssstik.io/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'x-browser-channel': 'stable',
        'x-browser-copyright': 'Copyright 2025 Google LLC. All rights reserved.',
        'x-browser-validation': '6h3XF8YcD8syi2FF2BbuE2KllQo=',
        'x-browser-year': '2025',
        'x-client-data': 'CJa2yQEIo7bJAQipncoBCNqAywEIkqHLAQiko8sBCIWgzQEY4eLOAQ==',
        # 'cookie': '__Secure-3PAPISID=fpdeMeMkm-8BgXFF/AKJAf2MT1fam6c56B; __Secure-3PSID=g.a000zwi29CRrQdhunDEqBS4x27STM60tWsr8w69loqfoTKCksqA981BGSzUxGEJHJuuCJW47yQACgYKAeASARMSFQHGX2Mi8NaTEOKHXjGJfRKXKXtM5RoVAUF8yKr9RjYkP0ITNiyUMV7d1LDj0076; __Secure-3PSIDTS=sidts-CjEB5H03P4TtkuMcWLOcBDwgVsodi9FV_vkbF7W8VhQXh9Ze4Er6P_K-UaYnqMm-zrI3EAA; NID=525=F9TP4JncIBm5shoSiN5ZvKzz8fQLhq2RG4JNnvuptumN9Oo60cewpQoBKry_hLqajuDaYyfYxeF4G2hJYV0SqYSdQcFs3Q78I6lOx6Zgb-bI9kM1woT5pUD6oxYnaOM7az_dXmd3XxxteB2ryKOthFrJXnLYhes4RDTw_a_9QobUV3KUG3GCtY0PM0SvAL7pEHB69NR_JPRNk66lTUIX0m0t4teqdYaWXCBqZyMXe5rh3BODuYB-_UTWodx-X82dBy4RSfXtyFY6UALLr_23VpRDLg2ZYzCht_grnagCv8h8rFqGp3NzKZNqzMh2Uo0FZl3hZtiHiCD4m1XZNotxyzYpwKTgLqKi5XUNm1VMvBKg4XPUrIRs3OMLARcvt30cvXiX1hD49T1kAD11lQEpRFe4NloSECQh3dUZGkOM5X_8ffzeJzgQbJUlXrqT1vgVmlasYcKjHX7bZJDEGT7wDhYb9SHzAqp1t-P_3B7y4fyEy_L91tZQCGUptXPix_lu-WiWVaRqXNJTUPzcFlwWuEMmY_wMl4HYu69LFYDOJySuGzE6usQMPUKNliPOR1dWP3oOsjCURRzCqr5TsvNrGyNupFxciOj5OZJRs2AlSeKv1JFre76gvRfQVMe-WBsw8pRc5sONk6ceuGYJIO_Sidij_QGJ26HHhGrK0GcWFGc5RrNbdBA9jrgD3xzM0xoQQqSpTud_tjha0nITYfpZjrwHv2yrI7NXBHAO-DCks-wBrSjT62BhlsvvYiuDFDzumw8JOKg88fuo20LpNyeIc30pvRukwu3ivsH8RRccrHrjEYUXaydPaMQ1Bp9qzqsSd2v3brUnkkVrQPMLis4M4M3Rd5MnrOAtNHE2wW-oDUDp3vjGeQra4h5DFcWdi0hGUHOHvN4iMfMrYNhHB9nJ8SJjp_KbqjEEPf6lRmewRDEaGPQiGHL1dUBaFEiV_HUIcC_AhRD1RgJiJvcCjuK16ma2A-Gm8rxcATe758mbnA_UdKfd1yW-Ph30PnYsMM7wvHZqYtGO94QvWAlUKdZXuRztMhXbD8shXrUm8-tMmzaKyDLawjRna3QbwhzG2-x6AWCWRbShrqZRLIS1imHwnW_XHvy5AGC27bAgEgGR0blZE9kPhxwC4o7auH2hEShVoeBPKKqPwcrCTwY_vWnj23ZNNAmHb4oCpE1eUOc3h0cgMKB1oroTiuL4G1UX2RUc5HfMrs1jLbKCN5fk8yjerem9KOOID1CdT6FlqxBl_Q; __Secure-3PSIDCC=AKEyXzW7SNa0xwpAWApSkXoVkIeF7InHzzylvC3ByQpSiL5Lvc2oPJN-ykhrULR7Mp4_isfQtDA',
    }

    response = requests.post(
        'https://analytics.google.com/g/collect?v=2&tid=G-ZSF3D6YSLC&gtm=45je5870h2v9115464968z8810593590za200zb810593590zd810593590&_p=1754830836756&gcd=13l3l3l3l1l1&npa=0&dma=0&tcfd=10000&tag_exp=101509157~103116026~103200004~103233427~104527907~104528501~104684208~104684211~104948813~105033766~105033768~105103161~105103163~105113531~105135708~105135710&cid=859323010.1754830598&ul=en-gb&sr=1536x864&uaa=x86&uab=64&uafvl=Not)A%253BBrand%3B8.0.0.0%7CChromium%3B138.0.7204.184%7CGoogle%2520Chrome%3B138.0.7204.184&uamb=0&uam=&uap=Windows&uapv=19.0.0&uaw=0&are=1&frm=0&pscdl=noapi&_eu=AAAAAAQ&_s=5&sid=1754830598&sct=1&seg=1&dl=https%3A%2F%2Fssstik.io%2F&dt=TikTok%20Downloader%20-%20Download%20TikTok%20Video%20Without%20Watermark&en=link-submit_supported-links&_c=1&ep.insertedLink=https%3A%2F%2Fwww.tiktok.com%2F%40tran_uy%2Fvideo%2F7531576627038375188%3Fis_from_webapp%3D1%26sender_device%3Dpc&_et=1687&tfd=22147',
        cookies=cookies,
        headers=headers,
    )


    cookies = {
        '_ga': 'GA1.1.859323010.1754830598',
        '__gads': 'ID=82edfe4d168befa6:T=1754830599:RT=1754830599:S=ALNI_MZ9N-cTi-5sA8NT6tQkT9d600pDyw',
        '__gpi': 'UID=0000117de1283bfb:T=1754830599:RT=1754830599:S=ALNI_Ma6z0HRteltZ1wxi8JAfTLmTtksGQ',
        '__eoi': 'ID=19384aa1fe27cb10:T=1754830599:RT=1754830599:S=AA-AfjY17XF9vcbYRJCP2HHRUubT',
        'FCNEC': '%5B%5B%22AKsRol-8h4Jy2MYOGVC6iPUHE-y7lnAPrbO_B5Ryu_a40aNc-j21bxRxCpZEaIcrQ-lKog4wALOn-ha90VHe_6aUIYs9n-i31uOeA6-ckjlQyb0Prh5ioqbtDYpRLC1htQxC1L5A_ky_I5SvFCIRAGMn8zM7rdwkBw%3D%3D%22%5D%5D',
        '_ga_ZSF3D6YSLC': 'GS2.1.s1754830598$o1$g1$t1754830858$j27$l0$h0',
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9,vi;q=0.8,en-US;q=0.7,zh-TW;q=0.6,zh;q=0.5',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'hx-current-url': 'https://ssstik.io/',
        'hx-request': 'true',
        'hx-target': 'target',
        'hx-trigger': '_gcaptcha_pt',
        'origin': 'https://ssstik.io',
        'priority': 'u=1, i',
        'referer': 'https://ssstik.io/',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        # 'cookie': '_ga=GA1.1.859323010.1754830598; __gads=ID=82edfe4d168befa6:T=1754830599:RT=1754830599:S=ALNI_MZ9N-cTi-5sA8NT6tQkT9d600pDyw; __gpi=UID=0000117de1283bfb:T=1754830599:RT=1754830599:S=ALNI_Ma6z0HRteltZ1wxi8JAfTLmTtksGQ; __eoi=ID=19384aa1fe27cb10:T=1754830599:RT=1754830599:S=AA-AfjY17XF9vcbYRJCP2HHRUubT; FCNEC=%5B%5B%22AKsRol-8h4Jy2MYOGVC6iPUHE-y7lnAPrbO_B5Ryu_a40aNc-j21bxRxCpZEaIcrQ-lKog4wALOn-ha90VHe_6aUIYs9n-i31uOeA6-ckjlQyb0Prh5ioqbtDYpRLC1htQxC1L5A_ky_I5SvFCIRAGMn8zM7rdwkBw%3D%3D%22%5D%5D; _ga_ZSF3D6YSLC=GS2.1.s1754830598$o1$g1$t1754830858$j27$l0$h0',
    }

    params = {
        'url': 'dl',
    }

    data = {
        'id': url,
        'locale': 'en',
        'tt': 'cGRpS0U_',
    }

    try:
        # Step 1: Request download page
        response = requests.post(
            'https://ssstik.io/abc',
            params=params,
            cookies=cookies,
            headers=headers,
            data=data,
            timeout=10
        )
        response.raise_for_status()

        # Step 2: Extract download link
        download_soup = BeautifulSoup(response.text, "html.parser")
        link_tag = download_soup.find("a", href=True)
        if not link_tag:
            return None, "No download link found."
        download_link = link_tag["href"]

        # Step 3: Download the video file
        video_name = extract_id_from_url(download_link)
        storage_path = os.path.join(save_dir, f"{video_name}.mp4")

        headers_dl = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://ssstik.io/",
        }
        with requests.get(download_link, headers=headers_dl, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            downloaded = 0

            with open(storage_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total and downloaded >= total:
                        break

        return storage_path, None

    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except OSError as e:
        return None, f"File error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"
    


def download_video_sstik(url: str, save_dir: str = os.path.join('storage', 'videos', 'downloaded')):
    """
    Download TikTok video using sstik.io service and upload to Supabase.
    Returns: (public_url, description, error)
    """

    os.makedirs(save_dir, exist_ok=True)

    try:
        # --- Download the video ---
        storage_path, error = _download_video_sstik_internal(url, save_dir)
        if error:
            return None, None, error

        # --- Extract video ID from filename ---
        video_id = os.path.basename(storage_path).split('_')[-1].split('.')[0]

        # --- Get video description ---
        # description = get_video_description(video_id)
        description = ""

        # --- Upload to Supabase ---
        upload_result = upload_video_to_bucket(storage_path)
        if upload_result is None:
            # File already exists, still return the public URL
            public_url = supabase.storage.from_("videobucket").get_public_url(os.path.basename(storage_path))
        else:
            public_url = supabase.storage.from_("videobucket").get_public_url(os.path.basename(storage_path))

        # Optionally remove local file
        # os.remove(storage_path)

        return public_url, description, None

    except Exception as e:
        return None, None, e