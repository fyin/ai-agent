import os
from typing import Optional

from sec_edgar_downloader import Downloader
import logging

from earning_report_analyst_agent.src.logger import configure_logging

logger = configure_logging(log_file = "log/er_analyst.log", module_name="earning_downloader", log_level=logging.INFO)

class SecDownloader:
    def __init__(self, company_name: str, email_address: str, download_folder: Optional[str] = None):
        self.company_name = company_name
        self.email_address = email_address
        self.download_folder = download_folder

    def download_recent_earning_report(self, ticker: Optional[str] = None, form_type:Optional[str]="10-Q", max_filings: Optional[int]=None,
                                       after: Optional[str] = None, before: Optional[str] = None) -> Optional[str]:
        """
        Download the most recent earnings report for stock ticker from SEC EDGAR.

        Args:
            form_type (str): SEC form type ('10-Q' or '8-K').
            max_filings (int): Number of filings to download (default: 1 for most recent).

        Returns:
            str: Path to the primary document (HTML) or None if failed.
        """
        try:
            if not os.path.exists(self.download_folder):
                os.makedirs(self.download_folder)

            dl = Downloader(company_name=self.download_folder,
                            email_address=self.email_address,
                            download_folder=self.download_folder)

            dl.get(form_type, ticker, limit=max_filings, after=after, before=before, include_amends=True, download_details=True)

            filing_dir = os.path.join(self.download_folder, "sec-edgar-filings", ticker, form_type)
            if not os.path.exists(filing_dir):
                raise ValueError(f"No {form_type} filings found for {ticker}.")

            # Get the most recent filing folder
            filing_folders = sorted([f for f in os.listdir(filing_dir) if os.path.isdir(os.path.join(filing_dir, f))],
                                    reverse=True)

            latest_filing = os.path.join(filing_dir, filing_folders[0], "primary-document.html")

            logger.info(f"Downloaded {form_type} filing to: {latest_filing}")
            return latest_filing
        except Exception:
            logger.exception(f"Error downloading {form_type} filing for {ticker}")
            return None

if __name__ == '__main__':
    downloader = SecDownloader("Individual Researcher", "fyin2012@gmail.com", "sec_filings")
    downloader.download_recent_earning_report(ticker="AAPL", form_type="10-Q", max_filings=1)