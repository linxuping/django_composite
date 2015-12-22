package com.app;

import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v7.app.ActionBarActivity;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;

import java.util.List;

public class MainActivity extends ActionBarActivity {
    private boolean letUserChoice = false;
    private String visitUrl = "http://192.168.10.102:9900/news";
    private String visitUrl2 = "http://100.84.93.22:9901/news";
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (savedInstanceState == null) {
            getSupportFragmentManager().beginTransaction()
                    .add(R.id.container, new PlaceholderFragment())
                    .commit();
        }
        if (letUserChoice) {
            doDefault();
        } else {
            choiceBrowserToVisitUrl(visitUrl);
            //choiceBrowserToVisitUrl(visitUrl2);
        }
        // 直接退出程序

        finish();
    }


    private void choiceBrowserToVisitUrl(String url) {
        boolean existUC = false, existOpera = false, existQQ = false, existDolphin = false, existSkyfire = false, existSteel = false, existGoogle = false;
        String ucPath = "", operaPath = "", qqPath = "", dolphinPath = "", skyfirePath = "", steelPath = "", googlePath = "";
        PackageManager packageMgr = getPackageManager();
        List<PackageInfo> list = packageMgr.getInstalledPackages(0);
        for (int i = 0; i < list.size(); i++) {
            PackageInfo info = list.get(i);
            String temp = info.packageName;
            if (temp.equals("com.uc.browser") || temp.equals("com.UCMobile")) {
                // 存在UC
                ucPath = temp;
                existUC = true;
            } else if (temp.equals("com.tencent.mtt")) {
                // 存在QQ
                qqPath = temp;
                existQQ = true;
            } else if (temp.equals("com.opera.mini.android")) {
                // 存在Opera
                operaPath = temp;
                existOpera = true;
            } else if (temp.equals("mobi.mgeek.TunnyBrowser")) {
                dolphinPath = temp;
                existDolphin = true;
            } else if (temp.equals("com.skyfire.browser")) {
                skyfirePath = temp;
                existSkyfire = true;
            } else if (temp.equals("com.kolbysoft.steel")) {
                steelPath = temp;
                existSteel = true;
            } else if (temp.equals("com.android.browser")) {
                // 存在GoogleBroser

                googlePath = temp;
                existGoogle = true;
            }
        }
        if (existUC) {
            gotoUrl(ucPath, url, packageMgr);
        } else if (existOpera) {
            gotoUrl(operaPath, url, packageMgr);
        } else if (existQQ) {
            gotoUrl(qqPath, url, packageMgr);
        } else if (existDolphin) {
            gotoUrl(dolphinPath, url, packageMgr);
        } else if (existSkyfire) {
            gotoUrl(skyfirePath, url, packageMgr);
        } else if (existSteel) {
            gotoUrl(steelPath, url, packageMgr);
        } else if (existGoogle) {
            gotoUrl(googlePath, url, packageMgr);
        } else {
            doDefault();
        }
    }
    private void gotoUrl(String packageName, String url,
                         PackageManager packageMgr) {
        try {
            Intent intent;
            intent = packageMgr.getLaunchIntentForPackage(packageName);
            intent.setAction(Intent.ACTION_VIEW);
            intent.addCategory(Intent.CATEGORY_DEFAULT);
            intent.setData(Uri.parse(url));
            startActivity(intent);
        } catch (Exception e) {
            // 在1.5及以前版本会要求catch(android.content.pm.PackageManager.NameNotFoundException)异常，该异常在1.5以后版本已取消。

            e.printStackTrace();
        }
    }
    private void doDefault() {
        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(visitUrl));
        startActivity(intent);
    }
    /** 直接启动UC，用于验证测试。 */
    private void showUCBrowser() {
        Intent intent = new Intent();
        intent.setClassName("com.uc.browser", "com.uc.browser.ActivityUpdate");
        intent.setAction(Intent.ACTION_VIEW);
        intent.addCategory(Intent.CATEGORY_DEFAULT);
        intent.setData(Uri.parse(visitUrl));
        startActivity(intent);
    }
    /** 直接启动QQ，用于验证测试。 */
    private void showQQBrowser() {
        Intent intent = new Intent();
        intent.setClassName("com.tencent.mtt", "com.tencent.mtt.MainActivity");
        intent.setAction(Intent.ACTION_VIEW);
        intent.addCategory(Intent.CATEGORY_DEFAULT);
        intent.setData(Uri.parse(visitUrl));
        startActivity(intent);
    }
    /** 直接启动Opera，用于验证测试。 */
    private void showOperaBrowser() {
        Intent intent = new Intent();
        intent.setClassName("com.opera.mini.android",
                "com.opera.mini.android.Browser");
        intent.setAction(Intent.ACTION_VIEW);
        intent.addCategory(Intent.CATEGORY_DEFAULT);
        intent.setData(Uri.parse(visitUrl));
        startActivity(intent);
    }
    /** 直接启动Dolphin Browser，用于验证测试。 */
    private void showDolphinBrowser() {
        // 方法一：

        // Intent intent = new Intent();

        // intent.setClassName("mobi.mgeek.TunnyBrowser",

        // "mobi.mgeek.TunnyBrowser.BrowserActivity");

        // intent.setAction(Intent.ACTION_VIEW);

        // intent.addCategory(Intent.CATEGORY_DEFAULT);

        // intent.setData(Uri.parse(visitUrl));

        // startActivity(intent);

        // 方法二：

        gotoUrl("mobi.mgeek.TunnyBrowser", visitUrl, getPackageManager());
    }
    /** 直接启动Skyfire Browser，用于验证测试。 */
    private void showSkyfireBrowser() {
        // 方法一：

        Intent intent = new Intent();
        intent.setClassName("com.skyfire.browser",
                "com.skyfire.browser.core.Main");
        intent.setAction(Intent.ACTION_VIEW);
        intent.addCategory(Intent.CATEGORY_DEFAULT);
        intent.setData(Uri.parse(visitUrl));
        startActivity(intent);
        // 方法二：

        // gotoUrl("com.skyfire.browser", visitUrl, getPackageManager());

    }
    /** 直接启动Steel Browser，用于验证测试。 */
    private void showSteelBrowser() {
        // 方法一：

        // Intent intent = new Intent();

        // intent.setClassName("com.kolbysoft.steel",

        // "com.kolbysoft.steel.Steel");

        // intent.setAction(Intent.ACTION_VIEW);

        // intent.addCategory(Intent.CATEGORY_DEFAULT);

        // intent.setData(Uri.parse(visitUrl));

        // startActivity(intent);

        // 方法二：

        gotoUrl("com.kolbysoft.steel", visitUrl, getPackageManager());
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    /**
     * A placeholder fragment containing a simple view.
     */
    public static class PlaceholderFragment extends Fragment {

        public PlaceholderFragment() {
        }

        @Override
        public View onCreateView(LayoutInflater inflater, ViewGroup container,
                Bundle savedInstanceState) {
            View rootView = inflater.inflate(R.layout.fragment_main, container, false);
            return rootView;
        }
    }

}
